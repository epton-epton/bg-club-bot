import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, MenuButtonDefault, MenuButtonWebApp, WebAppInfo
from redis.asyncio import Redis

from bgclub.config import get_settings
from bgclub.db import engine
from bgclub_bot.handlers import start
from bgclub_bot.i18n import get_messages, telegram_command_languages
from bgclub_bot.tasks.reminders import session_reminder_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_menu_button(bot: Bot) -> None:
    settings = get_settings()
    url = settings.miniapp_url
    if not url:
        await bot.set_chat_menu_button(menu_button=MenuButtonDefault())
        return

    texts = get_messages("en")
    logger.info("Setting menu button URL: %s", url)
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text=texts["menu_button"],
                web_app=WebAppInfo(url=url),
            )
        )
    except Exception:
        logger.exception(
            "Failed to set menu button (check MINIAPP_URL is valid HTTPS): %s",
            url,
        )


async def setup_bot_commands(bot: Bot) -> None:
    default_texts = get_messages("en")
    await bot.set_my_commands(
        [BotCommand(command="start", description=default_texts["start_command"])]
    )
    for telegram_lang, locale in telegram_command_languages().items():
        texts = get_messages(locale)
        await bot.set_my_commands(
            [BotCommand(command="start", description=texts["start_command"])],
            language_code=telegram_lang,
        )


async def main() -> None:
    settings = get_settings()
    redis = Redis.from_url(settings.redis_url)
    storage = RedisStorage(redis=redis)

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)
    dp.include_router(start.router)

    await setup_bot_commands(bot)
    await setup_menu_button(bot)

    reminder_task = asyncio.create_task(session_reminder_loop())

    logger.info("Bot started (miniapp_url=%s)", settings.miniapp_url or "(not set)")
    try:
        await dp.start_polling(bot)
    finally:
        reminder_task.cancel()
        try:
            await reminder_task
        except asyncio.CancelledError:
            pass
        await bot.session.close()
        await redis.aclose()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
