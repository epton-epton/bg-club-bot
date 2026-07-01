from typing import Literal

Locale = Literal["ru", "en", "ua"]


def map_language_code(code: str | None) -> Locale | None:
    normalized = (code or "").lower()
    if normalized.startswith("ru"):
        return "ru"
    if normalized.startswith("uk") or normalized.startswith("ua"):
        return "ua"
    if normalized.startswith("en"):
        return "en"
    return None


def resolve_locale(
    saved: str | None,
    telegram_language_code: str | None,
) -> Locale:
    if saved in ("ru", "en", "ua"):
        return saved
    from_telegram = map_language_code(telegram_language_code)
    if from_telegram is not None:
        return from_telegram
    return "en"
