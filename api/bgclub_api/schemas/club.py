from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClubOpenStatusOut(BaseModel):
    is_open: bool | None
    label: str


class ClubBaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    hours: str
    timezone: str
    open_status_override: str | None
    rules: str
    updated_at: datetime


class ClubOut(ClubBaseOut):
    open_status: ClubOpenStatusOut


class ClubUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, min_length=1, max_length=512)
    hours: str | None = None
    timezone: str | None = Field(default=None, min_length=1, max_length=64)
    open_status_override: str | None = Field(default=None, max_length=255)
    rules: str | None = None
    clear_status_override: bool = False
