from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.session import get_session
from bgclub.services.content import list_published_announcements
from bgclub_api.schemas.announcement import AnnouncementOut

router = APIRouter(tags=["announcements"])


@router.get("/announcements", response_model=list[AnnouncementOut])
async def get_announcements(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[AnnouncementOut]:
    announcements = await list_published_announcements(session, limit=limit)
    return [AnnouncementOut.model_validate(item) for item in announcements]
