import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bgclub.db.base import Base


class VisitSource(str, enum.Enum):
    membership = "membership"
    walk_in = "walk_in"


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    membership_id: Mapped[int | None] = mapped_column(
        ForeignKey("memberships.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source: Mapped[VisitSource] = mapped_column(
        Enum(VisitSource, name="visit_source"),
        nullable=False,
    )
    checked_in_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user = relationship("User", foreign_keys=[user_id], lazy="joined")
    membership = relationship("Membership", lazy="joined")
    created_by = relationship("User", foreign_keys=[created_by_id], lazy="joined")
