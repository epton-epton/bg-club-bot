from datetime import datetime
from typing import TypedDict

from bgclub.db.models.user import User
from bgclub.locale import Locale, resolve_locale


class StartMessages(TypedDict):
    friend: str
    welcome: str
    welcome_back: str
    intro: str
    notify_hint: str
    admin_role: str
    miniapp_hint: str
    menu_button: str
    start_command: str


class NotifyMessages(TypedDict):
    default_game_title: str
    guests: str
    players: str
    booking_admin_new_title: str
    booking_admin_open_app: str
    booking_confirmed_title: str
    booking_confirmed_footer: str
    booking_cancelled_title: str
    booking_cancelled_footer: str
    session_full_title: str
    session_full_footer: str
    session_full_admin: str
    session_full_admin_footer: str
    session_admin_new_title: str
    session_joined: str
    session_cancelled: str
    session_deleted: str
    session_reminder: str


_START: dict[Locale, StartMessages] = {
    "ru": {
        "friend": "друг",
        "welcome": "Добро пожаловать",
        "welcome_back": "С возвращением",
        "intro": "Это бот клуба настольных игр.",
        "notify_hint": "Здесь вы будете получать уведомления о столах и событиях.",
        "admin_role": "У вас роль <b>администратора</b>.",
        "miniapp_hint": (
            "Основной интерфейс — в Mini App (кнопка «Открыть клуб» слева от поля ввода)."
        ),
        "menu_button": "Открыть клуб",
        "start_command": "Начать",
    },
    "en": {
        "friend": "friend",
        "welcome": "Welcome",
        "welcome_back": "Welcome back",
        "intro": "This is the board game club bot.",
        "notify_hint": "Here you will receive notifications about tables and events.",
        "admin_role": "You have the <b>administrator</b> role.",
        "miniapp_hint": (
            "The main interface is in the Mini App (the «Open club» button to the left of the input field)."
        ),
        "menu_button": "Open club",
        "start_command": "Start",
    },
    "ua": {
        "friend": "друже",
        "welcome": "Ласкаво просимо",
        "welcome_back": "З поверненням",
        "intro": "Це бот клубу настільних ігор.",
        "notify_hint": "Тут ви отримуватимете сповіщення про столи та події.",
        "admin_role": "У вас роль <b>адміністратора</b>.",
        "miniapp_hint": (
            "Основний інтерфейс — у Mini App (кнопка «Відкрити клуб» зліва від поля вводу)."
        ),
        "menu_button": "Відкрити клуб",
        "start_command": "Почати",
    },
}

_NOTIFY: dict[Locale, NotifyMessages] = {
    "ru": {
        "default_game_title": "Игра",
        "guests": "{count} чел.",
        "players": "{current}/{max} игроков",
        "booking_admin_new_title": "📥 <b>Новая заявка на бронь</b>",
        "booking_admin_open_app": "Откройте админку в приложении.",
        "booking_confirmed_title": "✅ <b>Бронь подтверждена</b>",
        "booking_confirmed_footer": "Ждём вас в клубе!",
        "booking_cancelled_title": "❌ <b>Бронь отменена</b>",
        "booking_cancelled_footer": "Если это ошибка — напишите администратору клуба.",
        "session_full_title": "✅ Стол <b>{title}</b> собран!",
        "session_full_footer": "Встреча состоится — ждём вас в клубе.",
        "session_full_admin": "📋 Стол <b>{title}</b> полный ({max} игроков).",
        "session_full_admin_footer": "Встреча состоится.",
        "session_admin_new_title": "🪑 <b>Новый стол</b>",
        "session_joined": (
            "👋 <b>{name}</b> присоединился к столу <b>{title}</b>\n"
            "📅 {when}\n"
            "👥 {players}"
        ),
        "session_cancelled": "❌ Стол <b>{title}</b> отменён создателем.\n📅 {when}",
        "session_deleted": "❌ Стол <b>{title}</b> удалён администратором.\n📅 {when}",
        "session_reminder": (
            "⏰ Напоминание: стол <b>{title}</b> через {hours} ч.\n"
            "📅 {when}\n"
            "👥 {players}"
        ),
    },
    "en": {
        "default_game_title": "Game",
        "guests": "{count} people",
        "players": "{current}/{max} players",
        "booking_admin_new_title": "📥 <b>New table booking request</b>",
        "booking_admin_open_app": "Open the admin panel in the app.",
        "booking_confirmed_title": "✅ <b>Booking confirmed</b>",
        "booking_confirmed_footer": "We look forward to seeing you at the club!",
        "booking_cancelled_title": "❌ <b>Booking cancelled</b>",
        "booking_cancelled_footer": "If this is a mistake, please contact the club administrator.",
        "session_full_title": "✅ Table <b>{title}</b> is full!",
        "session_full_footer": "The session is on — see you at the club.",
        "session_full_admin": "📋 Table <b>{title}</b> is full ({max} players).",
        "session_full_admin_footer": "The session is on.",
        "session_admin_new_title": "🪑 <b>New table</b>",
        "session_joined": (
            "👋 <b>{name}</b> joined table <b>{title}</b>\n"
            "📅 {when}\n"
            "👥 {players}"
        ),
        "session_cancelled": "❌ Table <b>{title}</b> was cancelled by the host.\n📅 {when}",
        "session_deleted": "❌ Table <b>{title}</b> was removed by an administrator.\n📅 {when}",
        "session_reminder": (
            "⏰ Reminder: table <b>{title}</b> in {hours} h.\n"
            "📅 {when}\n"
            "👥 {players}"
        ),
    },
    "ua": {
        "default_game_title": "Гра",
        "guests": "{count} осіб",
        "players": "{current}/{max} гравців",
        "booking_admin_new_title": "📥 <b>Нова заявка на бронювання</b>",
        "booking_admin_open_app": "Відкрийте адмінку в застосунку.",
        "booking_confirmed_title": "✅ <b>Бронювання підтверджено</b>",
        "booking_confirmed_footer": "Чекаємо на вас у клубі!",
        "booking_cancelled_title": "❌ <b>Бронювання скасовано</b>",
        "booking_cancelled_footer": "Якщо це помилка — напишіть адміністратору клубу.",
        "session_full_title": "✅ Стіл <b>{title}</b> зібрано!",
        "session_full_footer": "Зустріч відбудеться — чекаємо на вас у клубі.",
        "session_full_admin": "📋 Стіл <b>{title}</b> повний ({max} гравців).",
        "session_full_admin_footer": "Зустріч відбудеться.",
        "session_admin_new_title": "🪑 <b>Новий стіл</b>",
        "session_joined": (
            "👋 <b>{name}</b> приєднався до столу <b>{title}</b>\n"
            "📅 {when}\n"
            "👥 {players}"
        ),
        "session_cancelled": "❌ Стіл <b>{title}</b> скасовано організатором.\n📅 {when}",
        "session_deleted": "❌ Стіл <b>{title}</b> видалено адміністратором.\n📅 {when}",
        "session_reminder": (
            "⏰ Нагадування: стіл <b>{title}</b> через {hours} год.\n"
            "📅 {when}\n"
            "👥 {players}"
        ),
    },
}

_TELEGRAM_COMMAND_LANGUAGES: dict[str, Locale] = {
    "ru": "ru",
    "en": "en",
    "uk": "ua",
}

_DATETIME_AT: dict[Locale, str] = {
    "ru": "в",
    "en": "at",
    "ua": "о",
}


def user_locale(user: User) -> Locale:
    saved = user.language.value if user.language else None
    return resolve_locale(saved, None)


def get_start_messages(locale: Locale) -> StartMessages:
    return _START[locale]


def get_notify_messages(locale: Locale) -> NotifyMessages:
    return _NOTIFY[locale]


def telegram_command_languages() -> dict[str, Locale]:
    return _TELEGRAM_COMMAND_LANGUAGES


def format_datetime(starts_at: datetime, locale: Locale) -> str:
    at_word = _DATETIME_AT[locale]
    return starts_at.astimezone().strftime(f"%d.%m.%Y {at_word} %H:%M")


def format_guests(locale: Locale, count: int) -> str:
    return get_notify_messages(locale)["guests"].format(count=count)


def format_players(locale: Locale, current: int, maximum: int) -> str:
    return get_notify_messages(locale)["players"].format(current=current, max=maximum)


def game_title_fallback(locale: Locale) -> str:
    return get_notify_messages(locale)["default_game_title"]
