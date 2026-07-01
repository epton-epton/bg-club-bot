from pydantic import BaseModel, ConfigDict, Field



from bgclub.db.models.user import UserLanguage, UserRole, UserTheme





class MeOut(BaseModel):

    model_config = ConfigDict(from_attributes=True)



    id: int

    telegram_id: int

    username: str | None

    first_name: str | None

    last_name: str | None

    role: UserRole

    language: UserLanguage | None = None

    theme: UserTheme | None = None





class MePreferencesUpdate(BaseModel):

    language: UserLanguage | None = Field(default=None)

    theme: UserTheme | None = Field(default=None)


