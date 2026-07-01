from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.config import get_settings
from bgclub.db.models.user import User, UserLanguage, UserRole, UserTheme
from bgclub.services.telegram_notify import format_user_name


async def get_or_create_user(
    session: AsyncSession,
    *,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
) -> tuple[User, bool]:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user is not None:
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        await session.commit()
        await session.refresh(user)
        return user, False

    role = UserRole.admin if telegram_id in get_settings().admin_ids else UserRole.guest
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        role=role,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user, True


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def list_guest_users(session: AsyncSession, *, limit: int = 100) -> list[User]:
    result = await session.execute(
        select(User)
        .where(User.role == UserRole.guest)
        .order_by(User.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def search_users(session: AsyncSession, *, query: str, limit: int = 20) -> list[User]:
    q = query.strip()
    if not q:
        return []

    filters = [
        User.username.ilike(f"%{q}%"),
        User.first_name.ilike(f"%{q}%"),
        User.last_name.ilike(f"%{q}%"),
    ]
    if q.isdigit():
        filters.append(User.telegram_id == int(q))

    result = await session.execute(
        select(User).where(or_(*filters)).order_by(User.first_name, User.username).limit(limit)
    )
    return list(result.scalars().all())


def user_display_name(user: User) -> str:
    return format_user_name(user)


async def update_user_preferences(
    session: AsyncSession,
    *,
    user: User,
    language: UserLanguage | None = None,
    theme: UserTheme | None = None,
    update_language: bool = False,
    update_theme: bool = False,
) -> User:
    if update_language:
        user.language = language
    if update_theme:
        user.theme = theme
    await session.commit()
    await session.refresh(user)
    return user
