from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.user import User
from bgclub.db.models.visit import Visit, VisitSource
from bgclub.services.memberships import (
    MembershipError,
    get_active_membership,
    use_membership_visit,
)


class VisitError(Exception):
    def __init__(self, message: str, code: str = "error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


async def list_user_visits(session: AsyncSession, user_id: int, *, limit: int = 50) -> list[Visit]:
    result = await session.execute(
        select(Visit)
        .where(Visit.user_id == user_id)
        .order_by(Visit.checked_in_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def list_recent_visits(session: AsyncSession, *, limit: int = 50) -> list[Visit]:
    result = await session.execute(
        select(Visit).order_by(Visit.checked_in_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def create_visit(
    session: AsyncSession,
    *,
    user: User,
    source: VisitSource,
    created_by: User,
    checked_in_at: datetime | None = None,
    note: str | None = None,
) -> Visit:
    when = checked_in_at or datetime.now(UTC)

    membership_id = None
    if source == VisitSource.membership:
        membership = await get_active_membership(session, user.id)
        if membership is None:
            raise VisitError("У пользователя нет активного абонемента", "no_active_membership")
        try:
            await use_membership_visit(session, membership=membership)
        except MembershipError as exc:
            raise VisitError(exc.message, exc.code) from exc
        membership_id = membership.id
    elif source != VisitSource.walk_in:
        raise VisitError("Неверный источник визита", "invalid_source")

    visit = Visit(
        user_id=user.id,
        membership_id=membership_id,
        source=source,
        checked_in_at=when,
        created_by_id=created_by.id,
        note=note,
    )
    session.add(visit)
    await session.commit()
    await session.refresh(visit)
    return visit
