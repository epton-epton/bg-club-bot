import logging
from dataclasses import dataclass

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.game import Game
from bgclub.services.bgg import fetch_game_image_url

logger = logging.getLogger(__name__)

BGG_FETCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; bg-club-bot/1.0)",
    "Referer": "https://boardgamegeek.com/",
}

LEGACY_IMAGE_MARKERS = ("/thumb/img/", "/micro.jpg")


@dataclass
class CoverImage:
    content: bytes
    media_type: str


def is_legacy_bgg_image_url(url: str) -> bool:
    return any(marker in url for marker in LEGACY_IMAGE_MARKERS)


async def ensure_game_image_url(session: AsyncSession, game: Game) -> str | None:
    url = game.image_url
    if (not url or is_legacy_bgg_image_url(url)) and game.bgg_id:
        fresh = await fetch_game_image_url(game.bgg_id)
        if fresh:
            game.image_url = fresh
            await session.commit()
            return fresh
    return url


async def fetch_cover_bytes(url: str) -> CoverImage | None:
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        response = await client.get(url, headers=BGG_FETCH_HEADERS)
        if response.status_code != 200:
            return None
        media_type = response.headers.get("content-type", "image/jpeg")
        if not media_type.startswith("image/"):
            return None
        return CoverImage(content=response.content, media_type=media_type)


async def get_game_cover(session: AsyncSession, game: Game) -> CoverImage | None:
    url = await ensure_game_image_url(session, game)
    if not url:
        return None

    cover = await fetch_cover_bytes(url)
    if cover is not None:
        return cover

    if game.bgg_id:
        fresh = await fetch_game_image_url(game.bgg_id)
        if fresh and fresh != url:
            game.image_url = fresh
            await session.commit()
            return await fetch_cover_bytes(fresh)

    logger.warning("Failed to fetch cover for game %s", game.id)
    return None
