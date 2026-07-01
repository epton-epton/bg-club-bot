from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.club_settings import ClubSettings
from bgclub.services.club_hours import parse_hours_text
from bgclub.services.content import get_club_settings


class ClubSettingsError(ValueError):
    pass


def validate_timezone(value: str) -> str:
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ClubSettingsError(f"Неизвестный часовой пояс: {value}") from exc
    return value


def validate_hours(value: str) -> str:
    text = value.strip()
    if not text:
        raise ClubSettingsError("Укажите часы работы")
    if not parse_hours_text(text):
        raise ClubSettingsError(
            "Не удалось разобрать расписание. Пример: Пн–Чт: 16:00–22:00"
        )
    return text


async def update_club_settings(
    session: AsyncSession,
    settings: ClubSettings,
    *,
    name: str | None = None,
    address: str | None = None,
    hours: str | None = None,
    timezone: str | None = None,
    open_status_override: str | None = None,
    rules: str | None = None,
    clear_status_override: bool = False,
) -> ClubSettings:
    if name is not None:
        settings.name = name.strip()
    if address is not None:
        settings.address = address.strip()
    if hours is not None:
        settings.hours = validate_hours(hours)
    if timezone is not None:
        settings.timezone = validate_timezone(timezone.strip())
    if clear_status_override:
        settings.open_status_override = None
    elif open_status_override is not None:
        override = open_status_override.strip()
        settings.open_status_override = override or None
    if rules is not None:
        settings.rules = rules.strip()

    await session.commit()
    await session.refresh(settings)
    return settings


async def get_or_create_club_settings(session: AsyncSession) -> ClubSettings:
    settings = await get_club_settings(session)
    if settings is None:
        raise ClubSettingsError("Настройки клуба не найдены")
    return settings
