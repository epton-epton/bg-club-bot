from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.user import User
from bgclub.db.session import get_session
from bgclub.services.users import get_user_by_id, user_display_name
from bgclub.services.visits import VisitError, create_visit, list_recent_visits
from bgclub_api.deps.auth import require_admin
from bgclub_api.schemas.visit import VisitCreate, VisitOut

router = APIRouter(prefix="/admin", tags=["admin"])


def _to_visit_out(visit) -> VisitOut:
    return VisitOut(
        id=visit.id,
        user_id=visit.user_id,
        user_name=user_display_name(visit.user) if visit.user else None,
        membership_id=visit.membership_id,
        source=visit.source,
        checked_in_at=visit.checked_in_at,
        note=visit.note,
        created_at=visit.created_at,
    )


@router.get("/visits", response_model=list[VisitOut])
async def get_admin_visits(
    limit: int = Query(default=50, ge=1, le=200),
    _admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> list[VisitOut]:
    visits = await list_recent_visits(session, limit=limit)
    return [_to_visit_out(v) for v in visits]


@router.post("/visits", response_model=VisitOut, status_code=201)
async def post_admin_visit(
    payload: VisitCreate,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> VisitOut:
    user = await get_user_by_id(session, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    try:
        visit = await create_visit(
            session,
            user=user,
            source=payload.source,
            created_by=admin,
            checked_in_at=payload.checked_in_at,
            note=payload.note,
        )
    except VisitError as exc:
        status = 409 if exc.code == "no_active_membership" else 400
        raise HTTPException(status_code=status, detail=exc.message) from exc
    return _to_visit_out(visit)
