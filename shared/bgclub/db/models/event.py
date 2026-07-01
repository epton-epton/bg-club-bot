import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from bgclub.db.base import Base


class EventType(str, enum.Enum):
    tournament = "tournament"
    open_game = "open_game"
    workshop = "workshop"
    other = "other"


class EventStatus(str, enum.Enum):
    published = "published"
    cancelled = "cancelled"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, name="event_type"),
        default=EventType.other,
        server_default=EventType.other.value,
    )
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus, name="event_status"),
        default=EventStatus.published,
        server_default=EventStatus.published.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
