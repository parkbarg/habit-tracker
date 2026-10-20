"""add unique index on lower goal name

Revision ID: c5442042b0f9
Revises: 3e9b9c843eae
Create Date: 2026-10-20 21:19:01.095286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5442042b0f9'
down_revision: Union[str, Sequence[str], None] = '3e9b9c843eae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "uq_goals_name_lower",
        "goals",
        [sa.text("lower(name)")],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("uq_goals_name_lower", table_name="goals")
