import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.game import Game
from bgclub.services.bgg import BggError, BggGameDetails, fetch_game


def _apply_bgg_details(target: Game, details: BggGameDetails) -> None:
    """Обновляет поля с BGG, не затирая уже сохранённые значения пустым ответом API."""
    target.bgg_id = details.bgg_id
    target.title = details.title
    if details.description is not None:
        target.description = details.description
    if details.players_min is not None:
        target.players_min = details.players_min
    if details.players_max is not None:
        target.players_max = details.players_max
    if details.duration_minutes is not None:
        target.duration_minutes = details.duration_minutes
    if details.image_url is not None:
        target.image_url = details.image_url
    if details.year_published is not None:
        target.year_published = details.year_published
    if details.bgg_rating is not None:
        target.bgg_rating = details.bgg_rating
    if details.bgg_rank is not None:
        target.bgg_rank = details.bgg_rank
    target.is_active = True


async def get_game_by_bgg_id(session: AsyncSession, bgg_id: int) -> Game | None:
    result = await session.execute(select(Game).where(Game.bgg_id == bgg_id))
    return result.scalar_one_or_none()


async def import_game_from_bgg(
    session: AsyncSession,
    bgg_id: int,
    *,
    game_id: int | None = None,
) -> Game:
    details = await fetch_game(bgg_id)
    existing_by_bgg = await get_game_by_bgg_id(session, bgg_id)

    if game_id is not None:
        target = await session.get(Game, game_id)
        if target is None:
            raise ValueError("Игра не найдена")
        if existing_by_bgg is not None and existing_by_bgg.id != game_id:
            raise ValueError("Эта игра BGG уже привязана к другой записи в каталоге")
    elif existing_by_bgg is not None:
        target = existing_by_bgg
    else:
        game = Game(
            bgg_id=details.bgg_id,
            title=details.title,
            description=details.description,
            players_min=details.players_min,
            players_max=details.players_max,
            duration_minutes=details.duration_minutes,
            image_url=details.image_url,
            year_published=details.year_published,
            bgg_rating=details.bgg_rating,
            bgg_rank=details.bgg_rank,
            is_active=True,
        )
        session.add(game)
        await session.commit()
        await session.refresh(game)
        return game

    _apply_bgg_details(target, details)
    await session.commit()
    await session.refresh(target)
    return target


async def create_manual_game(
    session: AsyncSession,
    *,
    title: str,
    description: str | None = None,
    players_min: int | None = None,
    players_max: int | None = None,
    duration_minutes: int | None = None,
) -> Game:
    game = Game(
        title=title,
        description=description,
        players_min=players_min,
        players_max=players_max,
        duration_minutes=duration_minutes,
        is_active=True,
    )
    session.add(game)
    await session.commit()
    await session.refresh(game)
    return game


async def import_games_from_bgg(session: AsyncSession, bgg_ids: list[int]) -> list[Game]:
    games: list[Game] = []
    for bgg_id in bgg_ids:
        try:
            games.append(await import_game_from_bgg(session, bgg_id))
        except (BggError, httpx.HTTPError):
            continue
    return games


async def list_all_games(session: AsyncSession) -> list[Game]:
    result = await session.execute(select(Game).order_by(Game.title))
    return list(result.scalars().all())


async def update_game(
    session: AsyncSession,
    game: Game,
    *,
    title: str | None = None,
    description: str | None = None,
    players_min: int | None = None,
    players_max: int | None = None,
    duration_minutes: int | None = None,
    is_active: bool | None = None,
) -> Game:
    if title is not None:
        game.title = title
    if description is not None:
        game.description = description
    if players_min is not None:
        game.players_min = players_min
    if players_max is not None:
        game.players_max = players_max
    if duration_minutes is not None:
        game.duration_minutes = duration_minutes
    if is_active is not None:
        game.is_active = is_active
    await session.commit()
    await session.refresh(game)
    return game


async def deactivate_game(session: AsyncSession, game: Game) -> Game:
    game.is_active = False
    await session.commit()
    await session.refresh(game)
    return game


async def sync_bgg_games(session: AsyncSession) -> tuple[int, int]:
    result = await session.execute(select(Game).where(Game.bgg_id.is_not(None), Game.is_active.is_(True)))
    games = list(result.scalars().all())
    synced = 0
    failed = 0
    for game in games:
        if game.bgg_id is None:
            continue
        try:
            await import_game_from_bgg(session, game.bgg_id)
            synced += 1
        except (BggError, httpx.HTTPError):
            failed += 1
    return synced, failed
