from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.table_booking import BookingStatus, TableBooking
from bgclub.db.models.user import User, UserRole
from bgclub.locale import Locale
from bgclub.services.telegram_notify import format_user_name, send_telegram_message
from bgclub.telegram_i18n import format_datetime, format_guests, get_notify_messages, user_locale


class BookingError(Exception):
    def __init__(self, message: str, code: str = "error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


async def _list_admins(session: AsyncSession) -> list[User]:
    result = await session.execute(select(User).where(User.role == UserRole.admin))
    return list(result.scalars().all())


def _build_admin_new_booking_text(
    locale: Locale,
    *,
    user_name: str,
    when: str,
    guest_count: int,
    note: str | None,
) -> str:
    texts = get_notify_messages(locale)
    note_line = f"\n💬 {note}" if note else ""
    return (
        f"{texts['booking_admin_new_title']}\n"
        f"👤 {user_name}\n"
        f"📅 {when}\n"
        f"👥 {format_guests(locale, guest_count)}{note_line}\n\n"
        f"{texts['booking_admin_open_app']}"
    )


def _build_user_booking_status_text(
    locale: Locale,
    *,
    when: str,
    guest_count: int,
    confirmed: bool,
) -> str:
    texts = get_notify_messages(locale)
    if confirmed:
        return (
            f"{texts['booking_confirmed_title']}\n"
            f"📅 {when}\n"
            f"👥 {format_guests(locale, guest_count)}\n\n"
            f"{texts['booking_confirmed_footer']}"
        )
    return (
        f"{texts['booking_cancelled_title']}\n"
        f"📅 {when}\n"
        f"👥 {format_guests(locale, guest_count)}\n\n"
        f"{texts['booking_cancelled_footer']}"
    )


async def _notify_admins_new_booking(session: AsyncSession, booking: TableBooking, user: User) -> None:
    user_name = format_user_name(user)
    for admin in await _list_admins(session):
        if admin.id == user.id:
            continue
        locale = user_locale(admin)
        when = format_datetime(booking.starts_at, locale)
        text = _build_admin_new_booking_text(
            locale,
            user_name=user_name,
            when=when,
            guest_count=booking.guest_count,
            note=booking.note,
        )
        await send_telegram_message(admin.telegram_id, text)


async def _notify_user_booking_status(booking: TableBooking, *, confirmed: bool) -> None:
    user = booking.user
    locale = user_locale(user)
    when = format_datetime(booking.starts_at, locale)
    text = _build_user_booking_status_text(
        locale,
        when=when,
        guest_count=booking.guest_count,
        confirmed=confirmed,
    )
    await send_telegram_message(user.telegram_id, text)


async def list_user_bookings(session: AsyncSession, user_id: int) -> list[TableBooking]:
    result = await session.execute(
        select(TableBooking)
        .where(TableBooking.user_id == user_id)
        .order_by(TableBooking.starts_at.desc())
    )
    return list(result.scalars().all())


async def list_all_bookings(
    session: AsyncSession,
    *,
    status: BookingStatus | None = None,
    limit: int = 100,
) -> list[TableBooking]:
    query = select(TableBooking).order_by(TableBooking.starts_at.desc()).limit(limit)
    if status is not None:
        query = query.where(TableBooking.status == status)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_booking_by_id(session: AsyncSession, booking_id: int) -> TableBooking | None:
    result = await session.execute(select(TableBooking).where(TableBooking.id == booking_id))
    return result.scalar_one_or_none()


async def create_booking(
    session: AsyncSession,
    *,
    user: User,
    starts_at: datetime,
    guest_count: int,
    note: str | None = None,
) -> TableBooking:
    if starts_at <= datetime.now(UTC):
        raise BookingError("Время брони должно быть в будущем", "starts_at_past")
    if guest_count < 1 or guest_count > 50:
        raise BookingError("Количество человек: от 1 до 50", "guest_count_invalid")

    booking = TableBooking(
        user_id=user.id,
        starts_at=starts_at,
        guest_count=guest_count,
        note=note,
    )
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    await _notify_admins_new_booking(session, booking, user)
    return booking


async def update_booking_status(
    session: AsyncSession,
    *,
    booking: TableBooking,
    status: BookingStatus,
) -> TableBooking:
    if booking.status == BookingStatus.cancelled:
        raise BookingError("Бронь уже отменена", "already_cancelled")
    if status == BookingStatus.submitted:
        raise BookingError("Нельзя вернуть статус «отправлена»", "invalid_status")

    previous_status = booking.status
    booking.status = status
    await session.commit()
    await session.refresh(booking)

    if previous_status != status:
        if status == BookingStatus.confirmed:
            await _notify_user_booking_status(booking, confirmed=True)
        elif status == BookingStatus.cancelled:
            await _notify_user_booking_status(booking, confirmed=False)

    return booking
