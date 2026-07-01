"""rename ember theme to daylight

Revision ID: 009
Revises: 008
Create Date: 2026-06-16

"""

from typing import Sequence, Union

from alembic import op

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE user_theme RENAME VALUE 'ember' TO 'daylight'")


def downgrade() -> None:
    op.execute("ALTER TYPE user_theme RENAME VALUE 'daylight' TO 'ember'")
