from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.user import User
from bgclub.db.session import get_session
from bgclub.services.memberships import (
    MembershipError,
    cancel_membership,
    create_membership,
    extend_membership,
    get_membership_by_id,
    list_active_memberships,
    visits_remaining,
)
from bgclub.services.users import get_user_by_id, user_display_name
from bgclub_api.deps.auth import require_admin
from bgclub_api.schemas.membership import MembershipCreate, MembershipExtend, MembershipOut

router = APIRouter(prefix="/admin", tags=["admin"])


def _to_membership_out(membership) -> MembershipOut:
    return MembershipOut(
        id=membership.id,
        user_id=membership.user_id,
        user_name=user_display_name(membership.user) if membership.user else None,
        total_visits=membership.total_visits,
        visits_used=membership.visits_used,
        visits_remaining=visits_remaining(membership),
        status=membership.status,
        note=membership.note,
        created_at=membership.created_at,
        updated_at=membership.updated_at,
    )


@router.get("/memberships", response_model=list[MembershipOut])
async def get_admin_memberships(
    _admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> list[MembershipOut]:
    memberships = await list_active_memberships(session)
    return [_to_membership_out(m) for m in memberships]


@router.post("/memberships", response_model=MembershipOut, status_code=201)
async def post_admin_membership(
    payload: MembershipCreate,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> MembershipOut:
    user = await get_user_by_id(session, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    try:
        membership = await create_membership(
            session,
            user=user,
            total_visits=payload.total_visits,
            issued_by=admin,
            note=payload.note,
        )
    except MembershipError as exc:
        status = 409 if exc.code == "active_membership_exists" else 400
        raise HTTPException(status_code=status, detail=exc.message) from exc
    return _to_membership_out(membership)


@router.patch("/memberships/{membership_id}/extend", response_model=MembershipOut)
async def patch_admin_membership_extend(
    membership_id: int,
    payload: MembershipExtend,
    _admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> MembershipOut:
    membership = await get_membership_by_id(session, membership_id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Абонемент не найден")
    try:
        updated = await extend_membership(session, membership=membership, add_visits=payload.add_visits)
    except MembershipError as exc:
        raise HTTPException(status_code=409, detail=exc.message) from exc
    return _to_membership_out(updated)


@router.patch("/memberships/{membership_id}/cancel", response_model=MembershipOut)
async def patch_admin_membership_cancel(
    membership_id: int,
    _admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> MembershipOut:
    membership = await get_membership_by_id(session, membership_id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Абонемент не найден")
    try:
        updated = await cancel_membership(session, membership=membership)
    except MembershipError as exc:
        raise HTTPException(status_code=409, detail=exc.message) from exc
    return _to_membership_out(updated)
