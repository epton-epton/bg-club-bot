from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from bgclub.db.models.visit import VisitSource


class VisitCreate(BaseModel):
    user_id: int
    source: VisitSource
    checked_in_at: datetime | None = None
    note: str | None = Field(default=None, max_length=1000)


class VisitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user_name: str | None = None
    membership_id: int | None
    source: VisitSource
    checked_in_at: datetime
    note: str | None
    created_at: datetime
