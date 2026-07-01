from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.table_booking import BookingStatus
from bgclub.db.session import get_session
from bgclub.services.bookings import BookingError, get_booking_by_id, list_all_bookings, update_booking_status
from bgclub.services.users import user_display_name
from bgclub_api.deps.auth import require_admin
from bgclub_api.routers.bookings import _to_booking_out
from bgclub_api.schemas.booking import BookingOut, BookingStatusUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/bookings", response_model=list[BookingOut])
async def get_admin_bookings(
    status: BookingStatus | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
    _admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> list[BookingOut]:
    bookings = await list_all_bookings(session, status=status, limit=limit)
    return [_to_booking_out(b) for b in bookings]


@router.patch("/bookings/{booking_id}", response_model=BookingOut)
async def patch_admin_booking(
    booking_id: int,
    payload: BookingStatusUpdate,
    _admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> BookingOut:
    booking = await get_booking_by_id(session, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Бронь не найдена")
    try:
        updated = await update_booking_status(session, booking=booking, status=payload.status)
    except BookingError as exc:
        raise HTTPException(status_code=409, detail=exc.message) from exc
    return _to_booking_out(updated)
