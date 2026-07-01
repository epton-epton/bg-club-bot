from bgclub.locale import Locale, resolve_locale
from bgclub.telegram_i18n import (
    StartMessages,
    get_start_messages,
    telegram_command_languages,
)

__all__ = [
    "BotMessages",
    "get_messages",
    "resolve_bot_locale",
    "telegram_command_languages",
]

BotMessages = StartMessages


def resolve_bot_locale(
    saved_language: str | None,
    telegram_language_code: str | None,
) -> Locale:
    return resolve_locale(saved_language, telegram_language_code)


def get_messages(locale: Locale) -> StartMessages:
    return get_start_messages(locale)
