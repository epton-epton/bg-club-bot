from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.game import Game
from bgclub.db.models.user import User
from bgclub.db.session import get_session
from bgclub.services.content import list_active_games
from bgclub.services.game_covers import get_game_cover
from bgclub.services.games import (
    create_manual_game,
    deactivate_game,
    list_all_games,
    sync_bgg_games,
    update_game,
)
from bgclub_api.deps.auth import require_admin
from bgclub_api.schemas.game import BggSyncResult, GameCreate, GameOut, GameUpdate

router = APIRouter(tags=["games"])


def _to_game_out(game: Game) -> GameOut:
    out = GameOut.model_validate(game)
    if game.image_url or game.bgg_id:
        out.cover_url = f"/api/v1/games/{game.id}/cover"
    return out


@router.get("/games", response_model=list[GameOut])
async def get_games(session: AsyncSession = Depends(get_session)) -> list[GameOut]:
    games = await list_active_games(session)
    return [_to_game_out(game) for game in games]


@router.get("/games/{game_id}/cover")
async def get_game_cover_endpoint(
    game_id: int,
    session: AsyncSession = Depends(get_session),
) -> Response:
    game = await session.get(Game, game_id)
    if game is None or not game.is_active:
        raise HTTPException(status_code=404, detail="Игра не найдена")

    cover = await get_game_cover(session, game)
    if cover is None:
        raise HTTPException(status_code=404, detail="Обложка не найдена")

    return Response(
        content=cover.content,
        media_type=cover.media_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/admin/games", response_model=list[GameOut])
async def list_admin_games(
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> list[GameOut]:
    games = await list_all_games(session)
    return [_to_game_out(game) for game in games]


@router.post("/games", response_model=GameOut, status_code=201)
async def create_game(
    payload: GameCreate,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> GameOut:
    game = await create_manual_game(session, **payload.model_dump())
    return _to_game_out(game)


@router.patch("/games/{game_id}", response_model=GameOut)
async def patch_game(
    game_id: int,
    payload: GameUpdate,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> GameOut:
    game = await session.get(Game, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Игра не найдена")
    game = await update_game(session, game, **payload.model_dump(exclude_unset=True))
    return _to_game_out(game)


@router.delete("/games/{game_id}", response_model=GameOut)
async def delete_game(
    game_id: int,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> GameOut:
    game = await session.get(Game, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Игра не найдена")
    game = await deactivate_game(session, game)
    return _to_game_out(game)


@router.post("/games/bgg/sync", response_model=BggSyncResult)
async def bgg_sync_all(
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> BggSyncResult:
    synced, failed = await sync_bgg_games(session)
    return BggSyncResult(synced=synced, failed=failed)
