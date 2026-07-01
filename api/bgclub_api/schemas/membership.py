from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from bgclub.db.models.membership import MembershipStatus


class MembershipCreate(BaseModel):
    user_id: int
    total_visits: int = Field(ge=1, le=500)
    note: str | None = Field(default=None, max_length=1000)


class MembershipExtend(BaseModel):
    add_visits: int = Field(ge=1, le=500)


class MembershipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user_name: str | None = None
    total_visits: int
    visits_used: int
    visits_remaining: int
    status: MembershipStatus
    note: str | None
    created_at: datetime
    updated_at: datetime
