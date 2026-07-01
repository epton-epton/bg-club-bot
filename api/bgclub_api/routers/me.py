from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.user import User
from bgclub.db.session import get_session
from bgclub.services.memberships import get_active_membership, visits_remaining
from bgclub.services.users import update_user_preferences, user_display_name
from bgclub.services.visits import list_user_visits
from bgclub_api.deps.auth import get_current_user
from bgclub_api.schemas.membership import MembershipOut
from bgclub_api.schemas.user import MeOut, MePreferencesUpdate
from bgclub_api.schemas.visit import VisitOut

router = APIRouter(tags=["me"])


@router.get("/me", response_model=MeOut)
async def get_me(user: User = Depends(get_current_user)) -> MeOut:
    return MeOut.model_validate(user)


@router.patch("/me/preferences", response_model=MeOut)
async def patch_my_preferences(
    payload: MePreferencesUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> MeOut:
    fields = payload.model_fields_set
    updated = await update_user_preferences(
        session,
        user=user,
        language=payload.language,
        theme=payload.theme,
        update_language="language" in fields,
        update_theme="theme" in fields,
    )
    return MeOut.model_validate(updated)


@router.get("/me/membership", response_model=MembershipOut | None)
async def get_my_membership(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> MembershipOut | None:
    membership = await get_active_membership(session, user.id)
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


@router.get("/me/visits", response_model=list[VisitOut])
async def get_my_visits(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[VisitOut]:
    visits = await list_user_visits(session, user.id, limit=limit)
    return [
        VisitOut(
            id=visit.id,
            user_id=visit.user_id,
            user_name=user_display_name(user),
            membership_id=visit.membership_id,
            source=visit.source,
            checked_in_at=visit.checked_in_at,
            note=visit.note,
            created_at=visit.created_at,
        )
        for visit in visits
    ]
