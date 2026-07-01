from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.models.game_session import SessionStatus
from bgclub.db.models.user import User
from bgclub.db.session import get_session
from bgclub.services.sessions import (
    SessionError,
    cancel_session,
    create_session,
    get_session_by_id,
    join_session,
    leave_session,
    list_sessions,
    session_game_title,
)
from bgclub.services.telegram_notify import format_user_name
from bgclub_api.deps.auth import get_current_user
from bgclub_api.schemas.session import SessionCreate, SessionOut, SessionParticipantOut

router = APIRouter(tags=["sessions"])


def _to_session_out(game_session, current_user: User) -> SessionOut:
    participants = [
        SessionParticipantOut(
            id=p.id,
            user_id=p.user_id,
            display_name=format_user_name(p.user),
            joined_at=p.joined_at,
        )
        for p in game_session.participants
    ]
    cover_url = None
    if game_session.game_id and game_session.game:
        if game_session.game.image_url or game_session.game.bgg_id:
            cover_url = f"/api/v1/games/{game_session.game_id}/cover"

    return SessionOut(
        id=game_session.id,
        game_id=game_session.game_id,
        game_title=game_session.game.title if game_session.game else None,
        custom_game_title=game_session.custom_game_title,
        title=session_game_title(game_session),
        starts_at=game_session.starts_at,
        max_players=game_session.max_players,
        participant_count=len(game_session.participants),
        status=game_session.status,
        note=game_session.note,
        creator_id=game_session.creator_id,
        creator_name=format_user_name(game_session.creator),
        is_creator=game_session.creator_id == current_user.id,
        is_joined=any(p.user_id == current_user.id for p in game_session.participants),
        cover_url=cover_url,
        participants=participants,
        created_at=game_session.created_at,
    )


def _session_error(exc: SessionError) -> HTTPException:
    status_map = {
        "game_required": 400,
        "game_conflict": 400,
        "starts_at_past": 400,
        "max_players_invalid": 400,
        "game_not_found": 404,
        "session_not_open": 409,
        "session_started": 409,
        "already_joined": 409,
        "session_full": 409,
        "session_cancelled": 409,
        "creator_cannot_leave": 409,
        "not_joined": 404,
        "not_creator": 403,
        "already_cancelled": 409,
    }
    return HTTPException(status_code=status_map.get(exc.code, 400), detail=exc.message)


@router.get("/sessions", response_model=list[SessionOut])
async def get_sessions(
    status: SessionStatus | None = Query(default=None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[SessionOut]:
    game_sessions = await list_sessions(session, status=status)
    return [_to_session_out(s, user) for s in game_sessions]


@router.post("/sessions", response_model=SessionOut, status_code=201)
async def post_session(
    payload: SessionCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SessionOut:
    try:
        game_session = await create_session(
            session,
            creator=user,
            game_id=payload.game_id,
            custom_game_title=payload.custom_game_title,
            starts_at=payload.starts_at,
            max_players=payload.max_players,
            note=payload.note,
        )
    except SessionError as exc:
        raise _session_error(exc) from exc
    return _to_session_out(game_session, user)


@router.post("/sessions/{session_id}/join", response_model=SessionOut)
async def post_session_join(
    session_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SessionOut:
    game_session = await get_session_by_id(session, session_id)
    if game_session is None:
        raise HTTPException(status_code=404, detail="Стол не найден")
    try:
        updated = await join_session(session, game_session=game_session, user=user)
    except SessionError as exc:
        raise _session_error(exc) from exc
    return _to_session_out(updated, user)


@router.delete("/sessions/{session_id}/leave", response_model=SessionOut)
async def delete_session_leave(
    session_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SessionOut:
    game_session = await get_session_by_id(session, session_id)
    if game_session is None:
        raise HTTPException(status_code=404, detail="Стол не найден")
    try:
        updated = await leave_session(session, game_session=game_session, user=user)
    except SessionError as exc:
        raise _session_error(exc) from exc
    return _to_session_out(updated, user)


@router.patch("/sessions/{session_id}/cancel", response_model=SessionOut)
async def patch_session_cancel(
    session_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SessionOut:
    game_session = await get_session_by_id(session, session_id)
    if game_session is None:
        raise HTTPException(status_code=404, detail="Стол не найден")
    try:
        updated = await cancel_session(session, game_session=game_session, user=user)
    except SessionError as exc:
        raise _session_error(exc) from exc
    return _to_session_out(updated, user)
