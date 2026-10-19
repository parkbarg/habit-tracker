from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from backend.db.session import engine

ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"


def test_upgrade_head_creates_goals_and_habit_records() -> None:
    config = Config(ALEMBIC_INI)

    # 空の状態から初期マイグレーションを適用して確認する
    command.downgrade(config, "base")
    command.upgrade(config, "head")

    inspector = inspect(engine)
    assert {"goals", "habit_records"} <= set(inspector.get_table_names())

    goal_columns = {column["name"] for column in inspector.get_columns("goals")}
    assert goal_columns == {"id", "name", "created_at", "updated_at"}

    record_columns = {
        column["name"] for column in inspector.get_columns("habit_records")
    }
    assert record_columns == {
        "id",
        "goal_id",
        "record_date",
        "status",
        "created_at",
        "updated_at",
    }
