import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bgclub.db.base import Base


class MembershipStatus(str, enum.Enum):
    active = "active"
    exhausted = "exhausted"
    cancelled = "cancelled"


class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    total_visits: Mapped[int] = mapped_column(Integer, nullable=False)
    visits_used: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus, name="membership_status"),
        default=MembershipStatus.active,
        server_default=MembershipStatus.active.value,
    )
    issued_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", foreign_keys=[user_id], lazy="joined")
    issued_by = relationship("User", foreign_keys=[issued_by_id], lazy="joined")
