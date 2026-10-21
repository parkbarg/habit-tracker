"""add on delete cascade to habit_records goal_id

Revision ID: 9eac5d21cf98
Revises: 916772c4e6fa
Create Date: 2026-10-21 23:20:36.746385

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9eac5d21cf98'
down_revision: Union[str, Sequence[str], None] = '916772c4e6fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


FK_NAME = "habit_records_goal_id_fkey"


def upgrade() -> None:
    """Upgrade schema."""
    # 目標の削除時に、その目標の記録もDB側で削除する
    op.drop_constraint(FK_NAME, "habit_records", type_="foreignkey")
    op.create_foreign_key(
        FK_NAME, "habit_records", "goals", ["goal_id"], ["id"], ondelete="CASCADE"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(FK_NAME, "habit_records", type_="foreignkey")
    op.create_foreign_key(FK_NAME, "habit_records", "goals", ["goal_id"], ["id"])
