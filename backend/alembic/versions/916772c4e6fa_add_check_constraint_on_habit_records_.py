"""add check constraint on habit_records status

Revision ID: 916772c4e6fa
Revises: 613b8b2f5576
Create Date: 2026-10-21 22:53:58.095281

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '916772c4e6fa'
down_revision: Union[str, Sequence[str], None] = '613b8b2f5576'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # マイグレーションは適用時点のスキーマを固定するため、Enumから生成せず値を直接書く
    op.create_check_constraint(
        "ck_habit_records_status", "habit_records", "status IN (1, 2, 3)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_habit_records_status", "habit_records", type_="check")
