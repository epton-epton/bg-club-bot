from pydantic import BaseModel, ConfigDict

from bgclub.db.models.user import UserRole


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    display_name: str
    role: UserRole
