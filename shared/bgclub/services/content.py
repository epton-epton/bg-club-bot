from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.announcement import Announcement, AnnouncementStatus
from bgclub.db.models.club_settings import ClubSettings
from bgclub.db.models.event import Event, EventStatus, EventType
from bgclub.db.models.game import Game


class ContentError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


async def get_club_settings(session: AsyncSession) -> ClubSettings | None:
    result = await session.execute(select(ClubSettings).limit(1))
    return result.scalar_one_or_none()


async def list_active_games(session: AsyncSession) -> list[Game]:
    result = await session.execute(
        select(Game).where(Game.is_active.is_(True)).order_by(Game.title)
    )
    return list(result.scalars().all())


async def list_published_announcements(
    session: AsyncSession,
    *,
    limit: int = 20,
) -> list[Announcement]:
    result = await session.execute(
        select(Announcement)
        .where(Announcement.status == AnnouncementStatus.published)
        .order_by(Announcement.is_pinned.desc(), Announcement.published_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def list_upcoming_events(
    session: AsyncSession,
    *,
    limit: int = 20,
) -> list[Event]:
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(Event)
        .where(
            Event.status == EventStatus.published,
            Event.starts_at >= now,
        )
        .order_by(Event.starts_at)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_feed(
    session: AsyncSession,
    *,
    events_limit: int = 5,
    announcements_limit: int = 5,
) -> tuple[list[Event], list[Announcement]]:
    events = await list_upcoming_events(session, limit=events_limit)
    announcements = await list_published_announcements(
        session,
        limit=announcements_limit,
    )
    return events, announcements


async def get_event_by_id(session: AsyncSession, event_id: int) -> Event | None:
    return await session.get(Event, event_id)


async def list_admin_events(
    session: AsyncSession,
    *,
    limit: int = 100,
) -> list[Event]:
    result = await session.execute(
        select(Event).order_by(Event.starts_at).limit(limit)
    )
    return list(result.scalars().all())


async def create_event(
    session: AsyncSession,
    *,
    title: str,
    description: str | None,
    starts_at: datetime,
    ends_at: datetime | None,
    event_type: EventType,
    status: EventStatus,
) -> Event:
    if ends_at is not None and ends_at < starts_at:
        raise ContentError("Время окончания не может быть раньше начала")
    event = Event(
        title=title,
        description=description,
        starts_at=starts_at,
        ends_at=ends_at,
        event_type=event_type,
        status=status,
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


async def update_event(
    session: AsyncSession,
    event: Event,
    *,
    title: str | None = None,
    description: str | None = None,
    starts_at: datetime | None = None,
    ends_at: datetime | None = None,
    event_type: EventType | None = None,
    status: EventStatus | None = None,
) -> Event:
    if title is not None:
        event.title = title
    if description is not None:
        event.description = description
    if starts_at is not None:
        event.starts_at = starts_at
    if ends_at is not None:
        event.ends_at = ends_at
    if event_type is not None:
        event.event_type = event_type
    if status is not None:
        event.status = status

    if event.ends_at is not None and event.ends_at < event.starts_at:
        raise ContentError("Время окончания не может быть раньше начала")

    await session.commit()
    await session.refresh(event)
    return event


async def delete_event(session: AsyncSession, event: Event) -> None:
    await session.delete(event)
    await session.commit()


async def get_announcement_by_id(
    session: AsyncSession,
    announcement_id: int,
) -> Announcement | None:
    return await session.get(Announcement, announcement_id)


async def list_admin_announcements(
    session: AsyncSession,
    *,
    limit: int = 100,
) -> list[Announcement]:
    result = await session.execute(
        select(Announcement)
        .order_by(Announcement.is_pinned.desc(), Announcement.published_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_announcement(
    session: AsyncSession,
    *,
    title: str,
    body: str,
    image_url: str | None,
    published_at: datetime | None,
    is_pinned: bool,
    status: AnnouncementStatus,
) -> Announcement:
    announcement = Announcement(
        title=title,
        body=body,
        image_url=image_url,
        published_at=published_at or datetime.now(timezone.utc),
        is_pinned=is_pinned,
        status=status,
    )
    session.add(announcement)
    await session.commit()
    await session.refresh(announcement)
    return announcement


async def update_announcement(
    session: AsyncSession,
    announcement: Announcement,
    *,
    title: str | None = None,
    body: str | None = None,
    image_url: str | None = None,
    published_at: datetime | None = None,
    is_pinned: bool | None = None,
    status: AnnouncementStatus | None = None,
) -> Announcement:
    if title is not None:
        announcement.title = title
    if body is not None:
        announcement.body = body
    if image_url is not None:
        announcement.image_url = image_url
    if published_at is not None:
        announcement.published_at = published_at
    if is_pinned is not None:
        announcement.is_pinned = is_pinned
    if status is not None:
        announcement.status = status

    await session.commit()
    await session.refresh(announcement)
    return announcement


async def delete_announcement(session: AsyncSession, announcement: Announcement) -> None:
    await session.delete(announcement)
    await session.commit()
