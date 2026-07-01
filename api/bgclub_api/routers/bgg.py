from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.user import User
from bgclub.db.session import get_session
from bgclub.services.bgg import BggError, search_games
from bgclub.services.games import import_game_from_bgg
from bgclub_api.deps.auth import require_admin
from bgclub_api.schemas.bgg import BggSearchItem
from bgclub_api.schemas.game import GameOut

router = APIRouter(tags=["games"])


@router.get("/games/bgg/search", response_model=list[BggSearchItem])
async def bgg_search(
    q: str = Query(min_length=2, max_length=100),
    _: User = Depends(require_admin),
) -> list[BggSearchItem]:
    try:
        results = await search_games(q)
    except BggError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return [BggSearchItem(bgg_id=r.bgg_id, title=r.title, year=r.year) for r in results]


@router.post("/games/bgg/{bgg_id}", response_model=GameOut)
async def bgg_import(
    bgg_id: int,
    game_id: int | None = Query(None, description="Привязать BGG к существующей игре в каталоге"),
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> GameOut:
    try:
        game = await import_game_from_bgg(session, bgg_id, game_id=game_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except BggError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    out = GameOut.model_validate(game)
    if game.image_url or game.bgg_id:
        out.cover_url = f"/api/v1/games/{game.id}/cover"
    return out
