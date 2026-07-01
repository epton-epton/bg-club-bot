from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bgclub.config import get_settings
from bgclub.db.models.game import Game
from bgclub.db.models.game_session import GameSession, SessionStatus
from bgclub.db.models.session_participant import SessionParticipant
from bgclub.db.models.user import User, UserRole
from bgclub.locale import Locale
from bgclub.services.telegram_notify import (
    format_user_name,
    notify_users_localized,
    send_telegram_message,
)
from bgclub.telegram_i18n import (
    format_datetime,
    format_players,
    game_title_fallback,
    get_notify_messages,
    user_locale,
)


class SessionError(Exception):
    def __init__(self, message: str, code: str = "error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


def session_game_title(game_session: GameSession, locale: Locale | None = None) -> str:
    if game_session.game is not None:
        return game_session.game.title
    if game_session.custom_game_title:
        return game_session.custom_game_title
    if locale is not None:
        return game_title_fallback(locale)
    return game_title_fallback("ru")


async def list_sessions(
    session: AsyncSession,
    *,
    status: SessionStatus | None = None,
    include_past: bool = False,
) -> list[GameSession]:
    query = (
        select(GameSession)
        .options(
            selectinload(GameSession.participants).selectinload(SessionParticipant.user),
            selectinload(GameSession.game),
            selectinload(GameSession.creator),
        )
        .order_by(GameSession.starts_at)
    )
    if status is not None:
        query = query.where(GameSession.status == status)
    else:
        query = query.where(GameSession.status.in_([SessionStatus.open, SessionStatus.full]))
    if not include_past:
        query = query.where(GameSession.starts_at > datetime.now(UTC))
    result = await session.execute(query)
    return list(result.scalars().unique().all())


async def get_session_by_id(session: AsyncSession, session_id: int) -> GameSession | None:
    result = await session.execute(
        select(GameSession)
        .where(GameSession.id == session_id)
        .options(
            selectinload(GameSession.participants).selectinload(SessionParticipant.user),
            selectinload(GameSession.game),
            selectinload(GameSession.creator),
        )
    )
    return result.scalar_one_or_none()


async def _get_admins(session: AsyncSession) -> list[User]:
    result = await session.execute(select(User).where(User.role == UserRole.admin))
    return list(result.scalars().all())


async def _notify_session_full(session: AsyncSession, game_session: GameSession) -> None:
    participants = [p.user for p in game_session.participants]

    def participant_text(locale: Locale) -> str:
        texts = get_notify_messages(locale)
        title = session_game_title(game_session, locale)
        when = format_datetime(game_session.starts_at, locale)
        players = format_players(locale, len(participants), game_session.max_players)
        return (
            f"{texts['session_full_title'].format(title=title)}\n"
            f"📅 {when}\n"
            f"👥 {players}\n\n"
            f"{texts['session_full_footer']}"
        )

    await notify_users_localized(participants, participant_text)

    admins = await _get_admins(session)
    notified_ids = {u.telegram_id for u in participants}
    for admin in admins:
        if admin.telegram_id in notified_ids:
            continue
        locale = user_locale(admin)
        texts = get_notify_messages(locale)
        title = session_game_title(game_session, locale)
        when = format_datetime(game_session.starts_at, locale)
        admin_text = (
            f"{texts['session_full_admin'].format(title=title, max=game_session.max_players)}\n"
            f"📅 {when}\n"
            f"{texts['session_full_admin_footer']}"
        )
        await send_telegram_message(admin.telegram_id, admin_text)


async def _notify_admins_new_session(
    session: AsyncSession,
    game_session: GameSession,
    creator: User,
) -> None:
    creator_name = format_user_name(creator)
    for admin in await _get_admins(session):
        if admin.id == creator.id:
            continue
        locale = user_locale(admin)
        texts = get_notify_messages(locale)
        title = session_game_title(game_session, locale)
        when = format_datetime(game_session.starts_at, locale)
        players = format_players(locale, 1, game_session.max_players)
        note_line = f"\n💬 {game_session.note}" if game_session.note else ""
        text = (
            f"{texts['session_admin_new_title']}\n"
            f"🎲 {title}\n"
            f"👤 {creator_name}\n"
            f"📅 {when}\n"
            f"👥 {players}{note_line}\n\n"
            f"{texts['booking_admin_open_app']}"
        )
        await send_telegram_message(admin.telegram_id, text)


async def create_session(
    session: AsyncSession,
    *,
    creator: User,
    game_id: int | None,
    custom_game_title: str | None,
    starts_at: datetime,
    max_players: int,
    note: str | None,
) -> GameSession:
    if game_id is None and not custom_game_title:
        raise SessionError("Укажите игру из каталога или название своей игры", "game_required")
    if game_id is not None and custom_game_title:
        raise SessionError("Укажите либо игру из каталога, либо свою игру", "game_conflict")
    if starts_at <= datetime.now(UTC):
        raise SessionError("Время начала должно быть в будущем", "starts_at_past")
    if max_players < 2:
        raise SessionError("Минимум 2 игрока", "max_players_invalid")

    if game_id is not None:
        game = await session.get(Game, game_id)
        if game is None or not game.is_active:
            raise SessionError("Игра не найдена", "game_not_found")

    game_session = GameSession(
        game_id=game_id,
        custom_game_title=custom_game_title.strip() if custom_game_title else None,
        starts_at=starts_at,
        max_players=max_players,
        note=note.strip() if note else None,
        creator_id=creator.id,
        status=SessionStatus.open,
    )
    session.add(game_session)
    await session.flush()

    participant = SessionParticipant(session_id=game_session.id, user_id=creator.id)
    session.add(participant)
    await session.commit()

    created = await get_session_by_id(session, game_session.id)
    assert created is not None
    await _notify_admins_new_session(session, created, creator)
    return created


async def join_session(
    session: AsyncSession,
    *,
    game_session: GameSession,
    user: User,
) -> GameSession:
    if game_session.status not in (SessionStatus.open,):
        raise SessionError("Стол недоступен для записи", "session_not_open")
    if game_session.starts_at <= datetime.now(UTC):
        raise SessionError("Стол уже начался", "session_started")

    already = any(p.user_id == user.id for p in game_session.participants)
    if already:
        raise SessionError("Вы уже записаны на этот стол", "already_joined")
    if len(game_session.participants) >= game_session.max_players:
        raise SessionError("Все места заняты", "session_full")

    session.add(SessionParticipant(session_id=game_session.id, user_id=user.id))
    became_full = len(game_session.participants) + 1 >= game_session.max_players
    if became_full:
        game_session.status = SessionStatus.full
    await session.commit()

    creator = game_session.creator
    if creator.id != user.id:
        locale = user_locale(creator)
        texts = get_notify_messages(locale)
        title = session_game_title(game_session, locale)
        when = format_datetime(game_session.starts_at, locale)
        players = format_players(
            locale,
            len(game_session.participants) + 1,
            game_session.max_players,
        )
        await send_telegram_message(
            creator.telegram_id,
            texts["session_joined"].format(name=format_user_name(user), title=title, when=when, players=players),
        )

    updated = await get_session_by_id(session, game_session.id)
    assert updated is not None
    if became_full:
        await _notify_session_full(session, updated)
    return updated


async def leave_session(
    session: AsyncSession,
    *,
    game_session: GameSession,
    user: User,
) -> GameSession:
    if game_session.status == SessionStatus.cancelled:
        raise SessionError("Стол отменён", "session_cancelled")
    if game_session.creator_id == user.id:
        raise SessionError("Создатель не может выйти — отмените стол", "creator_cannot_leave")

    participant = next((p for p in game_session.participants if p.user_id == user.id), None)
    if participant is None:
        raise SessionError("Вы не записаны на этот стол", "not_joined")

    await session.delete(participant)
    if game_session.status == SessionStatus.full:
        game_session.status = SessionStatus.open
    await session.commit()

    updated = await get_session_by_id(session, game_session.id)
    assert updated is not None
    return updated


async def cancel_session(
    session: AsyncSession,
    *,
    game_session: GameSession,
    user: User,
) -> GameSession:
    if game_session.creator_id != user.id:
        raise SessionError("Только создатель может отменить стол", "not_creator")
    if game_session.status == SessionStatus.cancelled:
        raise SessionError("Стол уже отменён", "already_cancelled")

    game_session.status = SessionStatus.cancelled
    await session.commit()

    participants = [p.user for p in game_session.participants if p.user_id != user.id]
    if participants:

        def cancelled_text(locale: Locale) -> str:
            texts = get_notify_messages(locale)
            title = session_game_title(game_session, locale)
            when = format_datetime(game_session.starts_at, locale)
            return texts["session_cancelled"].format(title=title, when=when)

        await notify_users_localized(participants, cancelled_text)

    updated = await get_session_by_id(session, game_session.id)
    assert updated is not None
    return updated


async def admin_delete_session(
    session: AsyncSession,
    *,
    game_session: GameSession,
) -> None:
    if game_session.status == SessionStatus.cancelled:
        raise SessionError("Стол уже отменён", "already_cancelled")

    participants = [p.user for p in game_session.participants]

    game_session.status = SessionStatus.cancelled
    await session.commit()

    if participants:

        def deleted_text(locale: Locale) -> str:
            texts = get_notify_messages(locale)
            title = session_game_title(game_session, locale)
            when = format_datetime(game_session.starts_at, locale)
            return texts["session_deleted"].format(title=title, when=when)

        await notify_users_localized(participants, deleted_text)


async def send_session_reminders(session: AsyncSession) -> int:
    settings = get_settings()
    hours = settings.session_reminder_hours
    now = datetime.now(UTC)
    window_start = now + timedelta(hours=hours) - timedelta(minutes=5)
    window_end = now + timedelta(hours=hours) + timedelta(minutes=5)

    result = await session.execute(
        select(GameSession)
        .where(
            GameSession.status.in_([SessionStatus.open, SessionStatus.full]),
            GameSession.reminder_sent_at.is_(None),
            GameSession.starts_at >= window_start,
            GameSession.starts_at <= window_end,
        )
        .options(
            selectinload(GameSession.participants).selectinload(SessionParticipant.user),
            selectinload(GameSession.game),
        )
    )
    game_sessions = list(result.scalars().unique().all())
    sent = 0

    for game_session in game_sessions:
        participants = [p.user for p in game_session.participants]

        def reminder_text(locale: Locale) -> str:
            texts = get_notify_messages(locale)
            title = session_game_title(game_session, locale)
            when = format_datetime(game_session.starts_at, locale)
            players = format_players(locale, len(participants), game_session.max_players)
            return texts["session_reminder"].format(
                title=title,
                hours=hours,
                when=when,
                players=players,
            )

        await notify_users_localized(participants, reminder_text)
        game_session.reminder_sent_at = now
        sent += 1

    if sent:
        await session.commit()
    return sent
