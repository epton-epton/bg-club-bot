from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.user import User
from bgclub.db.session import get_session
from bgclub.services.club_hours import compute_open_status, parse_hours_text
from bgclub.services.club_settings import ClubSettingsError, get_or_create_club_settings, update_club_settings
from bgclub_api.deps.auth import require_admin
from bgclub_api.schemas.club import ClubBaseOut, ClubOpenStatusOut, ClubOut, ClubUpdate

router = APIRouter(tags=["club"])


def _to_club_out(settings) -> ClubOut:
    status = compute_open_status(
        parse_hours_text(settings.hours),
        override=settings.open_status_override,
        club_timezone=settings.timezone,
    )
    base = ClubBaseOut.model_validate(settings)
    return ClubOut(
        **base.model_dump(),
        open_status=ClubOpenStatusOut(is_open=status.is_open, label=status.label),
    )


@router.patch("/admin/club", response_model=ClubOut)
async def patch_club(
    payload: ClubUpdate,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> ClubOut:
    settings = await get_or_create_club_settings(session)
    data = payload.model_dump(exclude_unset=True)
    clear_override = data.pop("clear_status_override", False)

    try:
        settings = await update_club_settings(
            session,
            settings,
            clear_status_override=clear_override,
            **data,
        )
    except ClubSettingsError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return _to_club_out(settings)
