from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.membership import Membership, MembershipStatus
from bgclub.db.models.user import User


class MembershipError(Exception):
    def __init__(self, message: str, code: str = "error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


def visits_remaining(membership: Membership) -> int:
    return max(0, membership.total_visits - membership.visits_used)


async def get_active_membership(session: AsyncSession, user_id: int) -> Membership | None:
    result = await session.execute(
        select(Membership)
        .where(
            Membership.user_id == user_id,
            Membership.status == MembershipStatus.active,
        )
        .order_by(Membership.created_at.desc())
        .limit(1)
    )
    membership = result.scalar_one_or_none()
    if membership is not None and visits_remaining(membership) == 0:
        membership.status = MembershipStatus.exhausted
        await session.commit()
        await session.refresh(membership)
        return None
    return membership


async def list_user_memberships(session: AsyncSession, user_id: int) -> list[Membership]:
    result = await session.execute(
        select(Membership)
        .where(Membership.user_id == user_id)
        .order_by(Membership.created_at.desc())
    )
    return list(result.scalars().all())


async def list_active_memberships(session: AsyncSession, *, limit: int = 100) -> list[Membership]:
    result = await session.execute(
        select(Membership)
        .where(
            Membership.status == MembershipStatus.active,
            Membership.visits_used < Membership.total_visits,
        )
        .order_by(Membership.updated_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_membership_by_id(session: AsyncSession, membership_id: int) -> Membership | None:
    result = await session.execute(select(Membership).where(Membership.id == membership_id))
    return result.scalar_one_or_none()


async def create_membership(
    session: AsyncSession,
    *,
    user: User,
    total_visits: int,
    issued_by: User,
    note: str | None = None,
) -> Membership:
    if total_visits < 1:
        raise MembershipError("Количество визитов должно быть ≥ 1", "total_visits_invalid")

    active = await get_active_membership(session, user.id)
    if active is not None:
        raise MembershipError(
            "У пользователя уже есть активный абонемент",
            "active_membership_exists",
        )

    membership = Membership(
        user_id=user.id,
        total_visits=total_visits,
        issued_by_id=issued_by.id,
        note=note,
    )
    session.add(membership)
    await session.commit()
    await session.refresh(membership)
    return membership


async def extend_membership(
    session: AsyncSession,
    *,
    membership: Membership,
    add_visits: int,
) -> Membership:
    if membership.status == MembershipStatus.cancelled:
        raise MembershipError("Абонемент отменён", "membership_cancelled")
    if add_visits < 1:
        raise MembershipError("Добавьте хотя бы 1 визит", "add_visits_invalid")

    membership.total_visits += add_visits
    if membership.status == MembershipStatus.exhausted:
        membership.status = MembershipStatus.active
    await session.commit()
    await session.refresh(membership)
    return membership


async def cancel_membership(session: AsyncSession, *, membership: Membership) -> Membership:
    if membership.status == MembershipStatus.cancelled:
        raise MembershipError("Абонемент уже отменён", "already_cancelled")

    membership.status = MembershipStatus.cancelled
    await session.commit()
    await session.refresh(membership)
    return membership


async def use_membership_visit(session: AsyncSession, *, membership: Membership) -> Membership:
    if membership.status != MembershipStatus.active:
        raise MembershipError("Абонемент не активен", "membership_not_active")
    if visits_remaining(membership) <= 0:
        raise MembershipError("Визиты на абонементе закончились", "no_visits_left")

    membership.visits_used += 1
    if visits_remaining(membership) == 0:
        membership.status = MembershipStatus.exhausted
    await session.commit()
    await session.refresh(membership)
    return membership
