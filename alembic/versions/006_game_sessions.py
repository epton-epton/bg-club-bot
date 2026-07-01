"""game sessions and participants

Revision ID: 006
Revises: 005
Create Date: 2026-06-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

session_status = postgresql.ENUM(
    "open",
    "full",
    "cancelled",
    "completed",
    name="session_status",
    create_type=False,
)


def upgrade() -> None:
    session_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "game_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=True),
        sa.Column("custom_game_title", sa.String(length=255), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("max_players", sa.Integer(), nullable=False),
        sa.Column("status", session_status, server_default="open", nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("creator_id", sa.Integer(), nullable=False),
        sa.Column("reminder_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["creator_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_game_sessions_starts_at"),
        "game_sessions",
        ["starts_at"],
        unique=False,
    )
    op.create_table(
        "session_participants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["session_id"], ["game_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "user_id", name="uq_session_participant"),
    )
    op.create_index(
        op.f("ix_session_participants_session_id"),
        "session_participants",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_session_participants_user_id"),
        "session_participants",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_session_participants_user_id"), table_name="session_participants")
    op.drop_index(op.f("ix_session_participants_session_id"), table_name="session_participants")
    op.drop_table("session_participants")
    op.drop_index(op.f("ix_game_sessions_starts_at"), table_name="game_sessions")
    op.drop_table("game_sessions")
    session_status.drop(op.get_bind(), checkfirst=True)
