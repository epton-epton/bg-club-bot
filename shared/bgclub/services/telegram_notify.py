import logging
from collections.abc import Callable
from functools import lru_cache

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bgclub.config import get_settings
from bgclub.db.models.user import User
from bgclub.locale import Locale
from bgclub.telegram_i18n import user_locale

logger = logging.getLogger(__name__)


@lru_cache
def get_bot() -> Bot:
    settings = get_settings()
    return Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def format_user_name(user: User) -> str:
    parts = [user.first_name, user.last_name]
    name = " ".join(p for p in parts if p)
    if name:
        return name
    if user.username:
        return f"@{user.username}"
    return f"ID {user.telegram_id}"


async def send_telegram_message(telegram_id: int, text: str) -> None:
    try:
        await get_bot().send_message(chat_id=telegram_id, text=text)
    except Exception:
        logger.exception("Failed to send telegram message to %s", telegram_id)


async def notify_users(users: list[User], text: str) -> None:
    for user in users:
        await send_telegram_message(user.telegram_id, text)


async def notify_users_localized(
    users: list[User],
    text_builder: Callable[[Locale], str],
) -> None:
    for user in users:
        await send_telegram_message(user.telegram_id, text_builder(user_locale(user)))
