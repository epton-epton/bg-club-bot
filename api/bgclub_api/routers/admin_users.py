from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.session import get_session
from bgclub.services.memberships import get_active_membership, visits_remaining
from bgclub.services.users import get_user_by_id, list_guest_users, search_users, user_display_name
from bgclub_api.deps.auth import require_admin
from bgclub_api.schemas.admin_user import AdminUserOut
from bgclub_api.schemas.membership import MembershipOut

router = APIRouter(prefix="/admin", tags=["admin"])


def _to_admin_user_out(user) -> AdminUserOut:
    return AdminUserOut(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        display_name=user_display_name(user),
        role=user.role,
    )


@router.get("/users", response_model=list[AdminUserOut])
async def get_admin_users(
    q: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=100),
    _admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> list[AdminUserOut]:
    if q and q.strip():
        users = await search_users(session, query=q.strip(), limit=limit)
    else:
        users = await list_guest_users(session, limit=limit)
    return [_to_admin_user_out(user) for user in users]


@router.get("/users/{user_id}/membership", response_model=MembershipOut | None)
async def get_admin_user_membership(
    user_id: int,
    _admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> MembershipOut | None:
    user = await get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    membership = await get_active_membership(session, user_id)
    if membership is None:
        return None
    return MembershipOut(
        id=membership.id,
        user_id=membership.user_id,
        user_name=user_display_name(user),
        total_visits=membership.total_visits,
        visits_used=membership.visits_used,
        visits_remaining=visits_remaining(membership),
        status=membership.status,
        note=membership.note,
        created_at=membership.created_at,
        updated_at=membership.updated_at,
    )
