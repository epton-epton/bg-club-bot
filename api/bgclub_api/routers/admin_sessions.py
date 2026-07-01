from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from bgclub.db.session import get_session
from bgclub.services.sessions import SessionError, admin_delete_session, get_session_by_id
from bgclub_api.deps.auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_admin_session(
    session_id: int,
    _admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> None:
    game_session = await get_session_by_id(session, session_id)
    if game_session is None:
        raise HTTPException(status_code=404, detail="Стол не найден")
    try:
        await admin_delete_session(session, game_session=game_session)
    except SessionError as exc:
        raise HTTPException(status_code=409, detail=exc.message) from exc
