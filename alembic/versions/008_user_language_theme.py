"""user language and theme preferences

Revision ID: 008
Revises: 007
Create Date: 2026-06-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_language = postgresql.ENUM("ru", "en", "ua", name="user_language", create_type=False)
user_theme = postgresql.ENUM(
    "synthwave",
    "midnight",
    "aurora",
    "ember",
    name="user_theme",
    create_type=False,
)


def upgrade() -> None:
    user_language.create(op.get_bind(), checkfirst=True)
    user_theme.create(op.get_bind(), checkfirst=True)
    op.add_column("users", sa.Column("language", user_language, nullable=True))
    op.add_column("users", sa.Column("theme", user_theme, nullable=True))


def downgrade() -> None:
    op.drop_column("users", "theme")
    op.drop_column("users", "language")
    user_theme.drop(op.get_bind(), checkfirst=True)
    user_language.drop(op.get_bind(), checkfirst=True)
