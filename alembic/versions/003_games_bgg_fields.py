"""games bgg fields

Revision ID: 003
Revises: 002
Create Date: 2026-06-06

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("games", sa.Column("bgg_id", sa.Integer(), nullable=True))
    op.add_column("games", sa.Column("image_url", sa.String(length=512), nullable=True))
    op.add_column("games", sa.Column("year_published", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_games_bgg_id"), "games", ["bgg_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_games_bgg_id"), table_name="games")
    op.drop_column("games", "year_published")
    op.drop_column("games", "image_url")
    op.drop_column("games", "bgg_id")
