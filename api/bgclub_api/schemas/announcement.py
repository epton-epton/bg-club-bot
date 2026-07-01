from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from bgclub.db.models.announcement import AnnouncementStatus


class AnnouncementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    image_url: str | None
    published_at: datetime
    is_pinned: bool
    status: AnnouncementStatus
    created_at: datetime


class AnnouncementCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)
    image_url: str | None = Field(default=None, max_length=1024)
    published_at: datetime | None = None
    is_pinned: bool = False
    status: AnnouncementStatus = AnnouncementStatus.published


class AnnouncementUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    body: str | None = Field(default=None, min_length=1)
    image_url: str | None = Field(default=None, max_length=1024)
    published_at: datetime | None = None
    is_pinned: bool | None = None
    status: AnnouncementStatus | None = None
