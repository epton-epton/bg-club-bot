from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from bgclub.config import get_settings
from bgclub.db import engine
from bgclub.services.media_uploads import ensure_upload_dirs
from bgclub_api.routers import (
    admin_bookings,
    admin_club,
    admin_content,
    admin_memberships,
    admin_sessions,
    admin_uploads,
    admin_users,
    admin_visits,
    announcements,
    bgg,
    bookings,
    club,
    events,
    feed,
    games,
    health,
    me,
    sessions,
)

API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    yield
    await engine.dispose()


app = FastAPI(
    title="bg-club-bot API",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
upload_root = Path(settings.upload_dir)
ensure_upload_dirs(upload_root)
app.mount("/uploads", StaticFiles(directory=str(upload_root)), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=API_PREFIX)
app.include_router(club.router, prefix=API_PREFIX)
app.include_router(bgg.router, prefix=API_PREFIX)
app.include_router(games.router, prefix=API_PREFIX)
app.include_router(announcements.router, prefix=API_PREFIX)
app.include_router(events.router, prefix=API_PREFIX)
app.include_router(feed.router, prefix=API_PREFIX)
app.include_router(me.router, prefix=API_PREFIX)
app.include_router(bookings.router, prefix=API_PREFIX)
app.include_router(sessions.router, prefix=API_PREFIX)
app.include_router(admin_sessions.router, prefix=API_PREFIX)
app.include_router(admin_bookings.router, prefix=API_PREFIX)
app.include_router(admin_memberships.router, prefix=API_PREFIX)
app.include_router(admin_visits.router, prefix=API_PREFIX)
app.include_router(admin_users.router, prefix=API_PREFIX)
app.include_router(admin_content.router, prefix=API_PREFIX)
app.include_router(admin_club.router, prefix=API_PREFIX)
app.include_router(admin_uploads.router, prefix=API_PREFIX)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "bg-club-bot-api", "docs": "/docs"}
