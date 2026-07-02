from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.is_file() else None,
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_bot_username: str = Field(default="", alias="TELEGRAM_BOT_USERNAME")
    miniapp_url: str = Field(default="", alias="MINIAPP_URL")
    cors_origins: str = Field(
        default="http://localhost:5173",
        alias="CORS_ORIGINS",
    )

    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")

    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    admin_telegram_ids: str = Field(default="", alias="ADMIN_TELEGRAM_IDS")

    session_reminder_hours: int = Field(default=1, alias="SESSION_REMINDER_HOURS")
    bgg_token: str = Field(default="", alias="BGG_TOKEN")

    dev_auth_enabled: bool = Field(default=False, alias="DEV_AUTH_ENABLED")
    dev_telegram_id: int = Field(default=999_999_001, alias="DEV_TELEGRAM_ID")

    upload_dir: str = Field(default="data/uploads", alias="UPLOAD_DIR")

    @field_validator("database_url", mode="before")
    @classmethod
    def ensure_asyncpg_driver(cls, value: str) -> str:
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @field_validator("miniapp_url", mode="after")
    @classmethod
    def normalize_miniapp_url(cls, value: str) -> str:
        value = value.strip().rstrip("/")
        if not value:
            return value
        if "://" in value:
            return value
        if value.startswith("localhost") or value.startswith("127.0.0.1"):
            return f"http://{value}"
        return f"https://{value}"

    @staticmethod
    def _normalize_cors_origin(origin: str) -> str:
        origin = origin.strip()
        if "://" in origin:
            return origin
        if origin.startswith("localhost") or origin.startswith("127.0.0.1"):
            return f"http://{origin}"
        return f"https://{origin}"

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            self._normalize_cors_origin(origin)
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def admin_ids(self) -> set[int]:
        if not self.admin_telegram_ids.strip():
            return set()
        return {int(x.strip()) for x in self.admin_telegram_ids.split(",") if x.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
