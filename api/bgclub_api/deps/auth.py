import json

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.auth.telegram import InitDataError, validate_init_data
from bgclub.config import get_settings
from bgclub.db.models.user import User, UserRole
from bgclub.db.session import get_session
from bgclub.services.users import get_or_create_user


async def get_current_user(
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")

    settings = get_settings()

    if authorization.startswith("dev"):
        if not settings.dev_auth_enabled:
            raise HTTPException(status_code=401, detail="Dev auth disabled")
        raw_id = authorization.removeprefix("dev").strip()
        telegram_id = int(raw_id) if raw_id else settings.dev_telegram_id
        user, _ = await get_or_create_user(
            session,
            telegram_id=telegram_id,
            username="dev_user",
            first_name="Dev",
            last_name="User",
        )
        return user

    if not authorization.startswith("tma "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    init_data = authorization.removeprefix("tma ").strip()

    try:
        parsed = validate_init_data(init_data, settings.telegram_bot_token)
        tg_user = json.loads(parsed["user"])
    except (InitDataError, KeyError, json.JSONDecodeError, TypeError) as exc:
        raise HTTPException(status_code=401, detail="Invalid init data") from exc

    user, _ = await get_or_create_user(
        session,
        telegram_id=int(tg_user["id"]),
        username=tg_user.get("username"),
        first_name=tg_user.get("first_name"),
        last_name=tg_user.get("last_name"),
    )
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user
