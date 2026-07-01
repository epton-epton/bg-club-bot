from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import MenuButtonWebApp, Message, WebAppInfo

from bgclub.config import get_settings
from bgclub.db.models.user import UserLanguage
from bgclub.db.session import async_session_factory
from bgclub.locale import map_language_code
from bgclub.services.users import get_or_create_user

from bgclub_bot.i18n import get_messages, resolve_bot_locale

router = Router()


def display_name(
    first_name: str | None,
    last_name: str | None,
    *,
    fallback: str,
) -> str:
    parts = [part for part in (first_name, last_name) if part]
    return " ".join(parts) if parts else fallback


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    if message.from_user is None:
        return

    async with async_session_factory() as session:
        user, created = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        if user.language is None:
            mapped = map_language_code(message.from_user.language_code)
            if mapped is not None:
                user.language = UserLanguage(mapped)
                await session.commit()
                await session.refresh(user)

    saved_language = user.language.value if user.language else None
    locale = resolve_bot_locale(saved_language, message.from_user.language_code)
    texts = get_messages(locale)

    name = display_name(
        message.from_user.first_name,
        message.from_user.last_name,
        fallback=texts["friend"],
    )
    greeting = texts["welcome"] if created else texts["welcome_back"]

    lines = [
        f"{greeting}, <b>{name}</b>!",
        "",
        texts["intro"],
        texts["notify_hint"],
    ]

    if user.role.value == "admin":
        lines.append("")
        lines.append(texts["admin_role"])

    lines.append("")
    lines.append(texts["miniapp_hint"])

    settings = get_settings()
    if settings.miniapp_url:
        await message.bot.set_chat_menu_button(
            chat_id=message.chat.id,
            menu_button=MenuButtonWebApp(
                text=texts["menu_button"],
                web_app=WebAppInfo(url=settings.miniapp_url),
            ),
        )

    await message.answer("\n".join(lines))
