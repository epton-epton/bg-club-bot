"""bookings, memberships, visits

Revision ID: 007
Revises: 006
Create Date: 2026-06-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

booking_status = postgresql.ENUM(
    "submitted",
    "confirmed",
    "cancelled",
    name="booking_status",
    create_type=False,
)
membership_status = postgresql.ENUM(
    "active",
    "exhausted",
    "cancelled",
    name="membership_status",
    create_type=False,
)
visit_source = postgresql.ENUM(
    "membership",
    "walk_in",
    name="visit_source",
    create_type=False,
)


def upgrade() -> None:
    booking_status.create(op.get_bind(), checkfirst=True)
    membership_status.create(op.get_bind(), checkfirst=True)
    visit_source.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "table_bookings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("guest_count", sa.Integer(), nullable=False),
        sa.Column("status", booking_status, server_default="submitted", nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_table_bookings_starts_at"), "table_bookings", ["starts_at"])
    op.create_index(op.f("ix_table_bookings_user_id"), "table_bookings", ["user_id"])

    op.create_table(
        "memberships",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("total_visits", sa.Integer(), nullable=False),
        sa.Column("visits_used", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", membership_status, server_default="active", nullable=False),
        sa.Column("issued_by_id", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["issued_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_memberships_user_id"), "memberships", ["user_id"])

    op.create_table(
        "visits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("membership_id", sa.Integer(), nullable=True),
        sa.Column("source", visit_source, nullable=False),
        sa.Column("checked_in_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["membership_id"], ["memberships.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_visits_checked_in_at"), "visits", ["checked_in_at"])
    op.create_index(op.f("ix_visits_membership_id"), "visits", ["membership_id"])
    op.create_index(op.f("ix_visits_user_id"), "visits", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_visits_user_id"), table_name="visits")
    op.drop_index(op.f("ix_visits_membership_id"), table_name="visits")
    op.drop_index(op.f("ix_visits_checked_in_at"), table_name="visits")
    op.drop_table("visits")
    op.drop_index(op.f("ix_memberships_user_id"), table_name="memberships")
    op.drop_table("memberships")
    op.drop_index(op.f("ix_table_bookings_user_id"), table_name="table_bookings")
    op.drop_index(op.f("ix_table_bookings_starts_at"), table_name="table_bookings")
    op.drop_table("table_bookings")
    visit_source.drop(op.get_bind(), checkfirst=True)
    membership_status.drop(op.get_bind(), checkfirst=True)
    booking_status.drop(op.get_bind(), checkfirst=True)
