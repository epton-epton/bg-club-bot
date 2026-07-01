import hashlib
import hmac
import json
import time
from typing import Any
from urllib.parse import parse_qsl


class InitDataError(Exception):
    pass


def validate_init_data(
    init_data: str,
    bot_token: str,
    *,
    max_age_seconds: int = 86_400,
) -> dict[str, Any]:
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise InitDataError("missing hash")

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise InitDataError("invalid hash")

    auth_date = int(parsed.get("auth_date", 0))
    if auth_date <= 0 or time.time() - auth_date > max_age_seconds:
        raise InitDataError("expired")

    return parsed


def parse_telegram_user(init_data: str, bot_token: str) -> dict[str, Any]:
    parsed = validate_init_data(init_data, bot_token)
    user_raw = parsed.get("user")
    if not user_raw:
        raise InitDataError("missing user")
    user = json.loads(user_raw)
    if "id" not in user:
        raise InitDataError("missing user id")
    return user
