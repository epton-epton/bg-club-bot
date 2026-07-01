"""public content tables

Revision ID: 002
Revises: 001
Create Date: 2026-06-06

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

announcement_status = postgresql.ENUM(
    "published", "draft", "archived", name="announcement_status", create_type=False
)
event_type = postgresql.ENUM(
    "tournament", "open_game", "workshop", "other", name="event_type", create_type=False
)
event_status = postgresql.ENUM(
    "published", "cancelled", name="event_status", create_type=False
)


def upgrade() -> None:
    announcement_status.create(op.get_bind(), checkfirst=True)
    event_type.create(op.get_bind(), checkfirst=True)
    event_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "club_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=512), nullable=False),
        sa.Column("hours", sa.Text(), nullable=False),
        sa.Column("rules", sa.Text(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "games",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("players_min", sa.Integer(), nullable=True),
        sa.Column("players_max", sa.Integer(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "announcements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_pinned", sa.Boolean(), server_default="false", nullable=False),
        sa.Column(
            "status",
            announcement_status,
            server_default="published",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "event_type",
            event_type,
            server_default="other",
            nullable=False,
        ),
        sa.Column(
            "status",
            event_status,
            server_default="published",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_starts_at"), "events", ["starts_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_events_starts_at"), table_name="events")
    op.drop_table("events")
    op.drop_table("announcements")
    op.drop_table("games")
    op.drop_table("club_settings")
    event_status.drop(op.get_bind(), checkfirst=True)
    event_type.drop(op.get_bind(), checkfirst=True)
    announcement_status.drop(op.get_bind(), checkfirst=True)
