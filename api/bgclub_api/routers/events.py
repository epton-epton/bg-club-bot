from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.session import get_session
from bgclub.services.content import list_upcoming_events
from bgclub_api.schemas.event import EventOut

router = APIRouter(tags=["events"])


@router.get("/events", response_model=list[EventOut])
async def get_events(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[EventOut]:
    events = await list_upcoming_events(session, limit=limit)
    return [EventOut.model_validate(event) for event in events]
