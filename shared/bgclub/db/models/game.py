from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from bgclub.db.base import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    bgg_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    year_published: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bgg_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    bgg_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    players_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    players_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
