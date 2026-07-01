from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bgclub.db.base import Base


class SessionParticipant(Base):
    __tablename__ = "session_participants"
    __table_args__ = (UniqueConstraint("session_id", "user_id", name="uq_session_participant"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("game_sessions.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    session = relationship("GameSession", back_populates="participants")
    user = relationship("User", lazy="joined")
