from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.ext.asyncio import AsyncSession



from bgclub.db.session import get_session

from bgclub.services.content import (

    ContentError,

    create_announcement,

    create_event,

    delete_announcement,

    delete_event,

    get_announcement_by_id,

    get_event_by_id,

    list_admin_announcements,

    list_admin_events,

    update_announcement,

    update_event,

)

from bgclub_api.deps.auth import require_admin

from bgclub_api.schemas.announcement import (

    AnnouncementCreate,

    AnnouncementOut,

    AnnouncementUpdate,

)

from bgclub_api.schemas.event import EventCreate, EventOut, EventUpdate



router = APIRouter(prefix="/admin", tags=["admin"])





@router.get("/events", response_model=list[EventOut])

async def list_admin_events_endpoint(

    _admin=Depends(require_admin),

    session: AsyncSession = Depends(get_session),

    limit: int = Query(default=100, ge=1, le=200),

) -> list[EventOut]:

    events = await list_admin_events(session, limit=limit)

    return [EventOut.model_validate(event) for event in events]





@router.post("/events", response_model=EventOut, status_code=201)

async def create_event_endpoint(

    payload: EventCreate,

    _admin=Depends(require_admin),

    session: AsyncSession = Depends(get_session),

) -> EventOut:

    try:

        event = await create_event(session, **payload.model_dump())

    except ContentError as exc:

        raise HTTPException(status_code=400, detail=exc.message) from exc

    return EventOut.model_validate(event)





@router.patch("/events/{event_id}", response_model=EventOut)

async def update_event_endpoint(

    event_id: int,

    payload: EventUpdate,

    _admin=Depends(require_admin),

    session: AsyncSession = Depends(get_session),

) -> EventOut:

    event = await get_event_by_id(session, event_id)

    if event is None:

        raise HTTPException(status_code=404, detail="Событие не найдено")

    try:

        event = await update_event(

            session,

            event,

            **payload.model_dump(exclude_unset=True),

        )

    except ContentError as exc:

        raise HTTPException(status_code=400, detail=exc.message) from exc

    return EventOut.model_validate(event)





@router.delete("/events/{event_id}", status_code=204)

async def delete_event_endpoint(

    event_id: int,

    _admin=Depends(require_admin),

    session: AsyncSession = Depends(get_session),

) -> None:

    event = await get_event_by_id(session, event_id)

    if event is None:

        raise HTTPException(status_code=404, detail="Событие не найдено")

    await delete_event(session, event)





@router.get("/announcements", response_model=list[AnnouncementOut])

async def list_admin_announcements_endpoint(

    _admin=Depends(require_admin),

    session: AsyncSession = Depends(get_session),

    limit: int = Query(default=100, ge=1, le=200),

) -> list[AnnouncementOut]:

    announcements = await list_admin_announcements(session, limit=limit)

    return [AnnouncementOut.model_validate(item) for item in announcements]





@router.post("/announcements", response_model=AnnouncementOut, status_code=201)

async def create_announcement_endpoint(

    payload: AnnouncementCreate,

    _admin=Depends(require_admin),

    session: AsyncSession = Depends(get_session),

) -> AnnouncementOut:

    announcement = await create_announcement(session, **payload.model_dump())

    return AnnouncementOut.model_validate(announcement)





@router.patch("/announcements/{announcement_id}", response_model=AnnouncementOut)

async def update_announcement_endpoint(

    announcement_id: int,

    payload: AnnouncementUpdate,

    _admin=Depends(require_admin),

    session: AsyncSession = Depends(get_session),

) -> AnnouncementOut:

    announcement = await get_announcement_by_id(session, announcement_id)

    if announcement is None:

        raise HTTPException(status_code=404, detail="Объявление не найдено")

    announcement = await update_announcement(

        session,

        announcement,

        **payload.model_dump(exclude_unset=True),

    )

    return AnnouncementOut.model_validate(announcement)





@router.delete("/announcements/{announcement_id}", status_code=204)

async def delete_announcement_endpoint(

    announcement_id: int,

    _admin=Depends(require_admin),

    session: AsyncSession = Depends(get_session),

) -> None:

    announcement = await get_announcement_by_id(session, announcement_id)

    if announcement is None:

        raise HTTPException(status_code=404, detail="Объявление не найдено")

    await delete_announcement(session, announcement)


