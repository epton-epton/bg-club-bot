from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.user import User
from bgclub.db.session import get_session
from bgclub.services.bookings import BookingError, create_booking, list_user_bookings
from bgclub.services.users import user_display_name
from bgclub_api.deps.auth import get_current_user
from bgclub_api.schemas.booking import BookingCreate, BookingOut

router = APIRouter(tags=["bookings"])


def _to_booking_out(booking) -> BookingOut:
    return BookingOut(
        id=booking.id,
        user_id=booking.user_id,
        user_name=user_display_name(booking.user) if booking.user else None,
        starts_at=booking.starts_at,
        guest_count=booking.guest_count,
        status=booking.status,
        note=booking.note,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


@router.get("/bookings/me", response_model=list[BookingOut])
async def get_my_bookings(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[BookingOut]:
    bookings = await list_user_bookings(session, user.id)
    return [_to_booking_out(b) for b in bookings]


@router.post("/bookings", response_model=BookingOut, status_code=201)
async def post_booking(
    payload: BookingCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> BookingOut:
    try:
        booking = await create_booking(
            session,
            user=user,
            starts_at=payload.starts_at,
            guest_count=payload.guest_count,
            note=payload.note,
        )
    except BookingError as exc:
        status = 400 if exc.code in {"starts_at_past", "guest_count_invalid"} else 400
        raise HTTPException(status_code=status, detail=exc.message) from exc
    return _to_booking_out(booking)
