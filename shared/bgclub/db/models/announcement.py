import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from bgclub.db.base import Base


class AnnouncementStatus(str, enum.Enum):
    published = "published"
    draft = "draft"
    archived = "archived"


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    status: Mapped[AnnouncementStatus] = mapped_column(
        Enum(AnnouncementStatus, name="announcement_status"),
        default=AnnouncementStatus.published,
        server_default=AnnouncementStatus.published.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
