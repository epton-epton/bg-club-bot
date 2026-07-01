from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from bgclub.db.models.table_booking import BookingStatus


class BookingCreate(BaseModel):
    starts_at: datetime
    guest_count: int = Field(ge=1, le=50)
    note: str | None = Field(default=None, max_length=1000)


class BookingStatusUpdate(BaseModel):
    status: BookingStatus


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user_name: str | None = None
    starts_at: datetime
    guest_count: int
    status: BookingStatus
    note: str | None
    created_at: datetime
    updated_at: datetime
