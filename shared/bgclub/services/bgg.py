import asyncio
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import unescape

import httpx

from bgclub.config import get_settings

BGG_API = "https://boardgamegeek.com/xmlapi2"
MAX_RETRIES = 12
RETRY_DELAY_SEC = 2


class BggError(Exception):
    pass


@dataclass
class BggSearchResult:
    bgg_id: int
    title: str
    year: int | None


@dataclass
class BggGameDetails:
    bgg_id: int
    title: str
    description: str | None
    players_min: int | None
    players_max: int | None
    duration_minutes: int | None
    image_url: str | None
    year_published: int | None
    bgg_rating: float | None
    bgg_rank: int | None


def _strip_html(value: str | None) -> str | None:
    if not value:
        return None
    text = unescape(re.sub(r"<[^>]+>", " ", value))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:2000] if text else None


def _int_or_none(value: str | None) -> int | None:
    if value is None or value == "" or value == "0":
        return None
    return int(value)


def _float_or_none(value: str | None) -> float | None:
    if value is None or value == "" or value == "0":
        return None
    return float(value)


def _value_attr(parent: ET.Element, tag: str) -> str | None:
    """BGG XML API хранит значения в атрибуте value, не в тексте тега."""
    el = parent.find(tag)
    if el is None:
        return None
    return el.get("value")


def _parse_bgg_stats(item: ET.Element) -> tuple[float | None, int | None]:
    ratings = item.find("statistics/ratings")
    if ratings is None:
        return None, None

    bgg_rating = _float_or_none(_value_attr(ratings, "bayesaverage"))
    bgg_rank = None
    for rank in ratings.findall("ranks/rank"):
        if rank.get("name") == "boardgame":
            value = rank.get("value", "")
            if value.isdigit():
                bgg_rank = int(value)
            break

    return bgg_rating, bgg_rank


def _bgg_headers() -> dict[str, str]:
    token = get_settings().bgg_token.strip()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


async def _fetch_xml(path: str, params: dict[str, str]) -> ET.Element:
    url = f"{BGG_API}/{path}"
    headers = _bgg_headers()
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        for _ in range(MAX_RETRIES):
            response = await client.get(url, params=params)
            if response.status_code == 202:
                await asyncio.sleep(RETRY_DELAY_SEC)
                continue
            if response.status_code in (401, 403):
                raise BggError(
                    "BGG API требует токен. Добавьте BGG_TOKEN в .env "
                    "(https://boardgamegeek.com/applications)"
                )
            if response.status_code >= 400:
                raise BggError(f"BGG API: HTTP {response.status_code}")
            return ET.fromstring(response.content)
    raise BggError("BGG API timeout — попробуйте позже")


async def search_games(query: str, *, limit: int = 20) -> list[BggSearchResult]:
    if not query.strip():
        return []

    root = await _fetch_xml("search", {"query": query.strip(), "type": "boardgame"})
    results: list[BggSearchResult] = []

    for item in root.findall("item"):
        if item.get("type") != "boardgame":
            continue
        bgg_id = int(item.get("id", "0"))
        name = item.find("name")
        year_el = item.find("yearpublished")
        if name is None:
            continue
        results.append(
            BggSearchResult(
                bgg_id=bgg_id,
                title=name.get("value", "").strip(),
                year=_int_or_none(year_el.get("value") if year_el is not None else None),
            )
        )
        if len(results) >= limit:
            break

    return results


async def fetch_game_image_url(bgg_id: int) -> str | None:
    """Актуальные URL обложек — через JSON API (старый XML отдаёт битые ссылки)."""
    url = "https://boardgamegeek.com/api/geekitems"
    params = {"objectid": str(bgg_id), "objecttype": "thing", "nosession": "1"}
    headers = {"User-Agent": "Mozilla/5.0 (compatible; bg-club-bot/1.0)"}

    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        response = await client.get(url, params=params)
        if response.status_code >= 400:
            return None
        item = response.json().get("item") or {}
        images = item.get("images") or {}
        for key in ("previewthumb", "square200", "imageurl", "thumb"):
            if key == "imageurl":
                value = item.get("imageurl")
            else:
                value = images.get(key)
            if isinstance(value, str) and value.startswith("http"):
                return value
        top = item.get("topimageurl")
        return top if isinstance(top, str) and top.startswith("http") else None


async def fetch_game(bgg_id: int) -> BggGameDetails:
    root = await _fetch_xml("thing", {"id": str(bgg_id), "stats": "1"})
    item = root.find("item")
    if item is None:
        raise BggError(f"Игра BGG #{bgg_id} не найдена")

    title = ""
    for name in item.findall("name"):
        if name.get("type") == "primary":
            title = name.get("value", "").strip()
            break
    if not title and item.findall("name"):
        title = item.findall("name")[0].get("value", "").strip()

    description = _strip_html(item.findtext("description"))
    image_url = await fetch_game_image_url(bgg_id)
    if not image_url:
        image_url = item.findtext("image") or item.findtext("thumbnail")
    bgg_rating, bgg_rank = _parse_bgg_stats(item)

    return BggGameDetails(
        bgg_id=bgg_id,
        title=title or f"BGG #{bgg_id}",
        description=description,
        players_min=_int_or_none(_value_attr(item, "minplayers")),
        players_max=_int_or_none(_value_attr(item, "maxplayers")),
        duration_minutes=_int_or_none(_value_attr(item, "playingtime")),
        image_url=image_url or None,
        year_published=_int_or_none(_value_attr(item, "yearpublished")),
        bgg_rating=bgg_rating,
        bgg_rank=bgg_rank,
    )
