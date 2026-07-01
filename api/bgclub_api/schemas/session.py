from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from bgclub.db.models.game_session import SessionStatus


class SessionParticipantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    display_name: str
    joined_at: datetime


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game_id: int | None
    game_title: str | None
    custom_game_title: str | None
    title: str
    starts_at: datetime
    max_players: int
    participant_count: int
    status: SessionStatus
    note: str | None
    creator_id: int
    creator_name: str
    is_creator: bool
    is_joined: bool
    cover_url: str | None = None
    participants: list[SessionParticipantOut]
    created_at: datetime


class SessionCreate(BaseModel):
    game_id: int | None = None
    custom_game_title: str | None = Field(default=None, max_length=255)
    starts_at: datetime
    max_players: int = Field(ge=2, le=20)
    note: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_game_source(self) -> "SessionCreate":
        has_catalog = self.game_id is not None
        has_custom = bool(self.custom_game_title and self.custom_game_title.strip())
        if not has_catalog and not has_custom:
            raise ValueError("Укажите игру из каталога или название своей игры")
        if has_catalog and has_custom:
            raise ValueError("Укажите либо игру из каталога, либо свою игру")
        return self
