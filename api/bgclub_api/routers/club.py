from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.session import get_session
from bgclub.services.club_hours import compute_open_status, parse_hours_text
from bgclub.services.content import get_club_settings
from bgclub_api.schemas.club import ClubBaseOut, ClubOpenStatusOut, ClubOut

router = APIRouter(tags=["club"])


@router.get("/club", response_model=ClubOut)
async def get_club(session: AsyncSession = Depends(get_session)) -> ClubOut:
    settings = await get_club_settings(session)
    if settings is None:
        raise HTTPException(status_code=404, detail="Club settings not configured")

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
