from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from bgclub.db.models.event import EventStatus, EventType


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    starts_at: datetime
    ends_at: datetime | None
    event_type: EventType
    status: EventStatus
    created_at: datetime


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    starts_at: datetime
    ends_at: datetime | None = None
    event_type: EventType = EventType.other
    status: EventStatus = EventStatus.published


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    event_type: EventType | None = None
    status: EventStatus | None = None
