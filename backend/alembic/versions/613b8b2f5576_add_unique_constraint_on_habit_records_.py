"""add unique constraint on habit_records goal_id and record_date

Revision ID: 613b8b2f5576
Revises: c5442042b0f9
Create Date: 2026-10-21 22:33:28.691402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '613b8b2f5576'
down_revision: Union[str, Sequence[str], None] = 'c5442042b0f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "uq_habit_records_goal_id_record_date",
        "habit_records",
        ["goal_id", "record_date"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_habit_records_goal_id_record_date", "habit_records", type_="unique"
    )
