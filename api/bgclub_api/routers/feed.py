from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.session import get_session
from bgclub.services.content import get_feed
from bgclub_api.schemas.announcement import AnnouncementOut
from bgclub_api.schemas.event import EventOut
from bgclub_api.schemas.feed import FeedOut

router = APIRouter(tags=["feed"])


@router.get("/feed", response_model=FeedOut)
async def get_feed_endpoint(
    session: AsyncSession = Depends(get_session),
    events_limit: int = Query(default=5, ge=1, le=20),
    announcements_limit: int = Query(default=5, ge=1, le=20),
) -> FeedOut:
    events, announcements = await get_feed(
        session,
        events_limit=events_limit,
        announcements_limit=announcements_limit,
    )
    return FeedOut(
        events=[EventOut.model_validate(event) for event in events],
        announcements=[
            AnnouncementOut.model_validate(item) for item in announcements
        ],
    )
