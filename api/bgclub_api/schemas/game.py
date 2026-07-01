from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GameOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bgg_id: int | None
    title: str
    image_url: str | None
    year_published: int | None
    bgg_rating: float | None
    bgg_rank: int | None
    description: str | None
    players_min: int | None
    players_max: int | None
    duration_minutes: int | None
    is_active: bool
    cover_url: str | None = None
    created_at: datetime
    updated_at: datetime


class GameCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    players_min: int | None = Field(default=None, ge=1)
    players_max: int | None = Field(default=None, ge=1)
    duration_minutes: int | None = Field(default=None, ge=1)


class GameUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    players_min: int | None = Field(default=None, ge=1)
    players_max: int | None = Field(default=None, ge=1)
    duration_minutes: int | None = Field(default=None, ge=1)
    is_active: bool | None = None


class BggSyncResult(BaseModel):
    synced: int
    failed: int
