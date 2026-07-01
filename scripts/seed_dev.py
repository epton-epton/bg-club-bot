"""Заполнить БД тестовыми данными для разработки."""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared"))

from sqlalchemy import func, select

from bgclub.db.models.announcement import Announcement, AnnouncementStatus
from bgclub.db.models.club_settings import ClubSettings
from bgclub.db.models.event import Event, EventStatus, EventType
from bgclub.db.session import async_session_factory, engine

DEFAULT_HOURS = "Пн–Чт: 16:00–22:00\nПт–Вс: 12:00–23:00"


async def seed() -> None:
    now = datetime.now(timezone.utc)

    async with async_session_factory() as session:
        club = await session.get(ClubSettings, 1)
        if club is None:
            session.add(
                ClubSettings(
                    id=1,
                    name="Клуб настольных игр",
                    address="ул. Примерная, 1",
                    hours=DEFAULT_HOURS,
                    timezone="Europe/Kyiv",
                    rules=(
                        "Уважайте других игроков.\n"
                        "После игры верните компоненты на место.\n"
                        "Напитки — только в зоне отдыха."
                    ),
                )
            )
        else:
            club.hours = DEFAULT_HOURS
            club.timezone = "Europe/Kyiv"

        announcements_count = await session.scalar(
            select(func.count()).select_from(Announcement)
        )
        if not announcements_count:
            session.add_all(
                [
                    Announcement(
                        title="Новые игры в каталоге",
                        body="Пополнили полку: Azul, Splendor и Wingspan.",
                        image_url=None,
                        published_at=now - timedelta(days=1),
                        is_pinned=True,
                        status=AnnouncementStatus.published,
                    ),
                    Announcement(
                        title="Расписание на выходные",
                        body="В субботу открываемся с 12:00. Бронируйте столы заранее.",
                        published_at=now - timedelta(days=3),
                        status=AnnouncementStatus.published,
                    ),
                ]
            )

        events_count = await session.scalar(select(func.count()).select_from(Event))
        if not events_count:
            session.add_all(
                [
                    Event(
                        title="Турнир по Catan",
                        description="Регистрация на месте. Приходите за 15 минут до старта.",
                        starts_at=now + timedelta(days=7, hours=18),
                        ends_at=now + timedelta(days=7, hours=22),
                        event_type=EventType.tournament,
                        status=EventStatus.published,
                    ),
                    Event(
                        title="Вечер настолок для новичков",
                        description="Познакомим с базовыми играми клуба.",
                        starts_at=now + timedelta(days=3, hours=19),
                        ends_at=now + timedelta(days=3, hours=22),
                        event_type=EventType.open_game,
                        status=EventStatus.published,
                    ),
                ]
            )

        await session.commit()

    await engine.dispose()
    print("Seed completed.")


if __name__ == "__main__":
    asyncio.run(seed())
