"""club status fields and announcement image

Revision ID: 005
Revises: 004
Create Date: 2026-06-07

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "club_settings",
        sa.Column("timezone", sa.String(length=64), server_default="Europe/Kyiv", nullable=False),
    )
    op.add_column(
        "club_settings",
        sa.Column("open_status_override", sa.String(length=255), nullable=True),
    )
    op.add_column("announcements", sa.Column("image_url", sa.String(length=1024), nullable=True))


def downgrade() -> None:
    op.drop_column("announcements", "image_url")
    op.drop_column("club_settings", "open_status_override")
    op.drop_column("club_settings", "timezone")
