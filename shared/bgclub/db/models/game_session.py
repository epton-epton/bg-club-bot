import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bgclub.db.base import Base


class SessionStatus(str, enum.Enum):
    open = "open"
    full = "full"
    cancelled = "cancelled"
    completed = "completed"


class GameSession(Base):
    __tablename__ = "game_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int | None] = mapped_column(
        ForeignKey("games.id", ondelete="SET NULL"),
        nullable=True,
    )
    custom_game_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    max_players: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, name="session_status"),
        default=SessionStatus.open,
        server_default=SessionStatus.open.value,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    reminder_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    game = relationship("Game", lazy="joined")
    creator = relationship("User", lazy="joined")
    participants = relationship(
        "SessionParticipant",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
