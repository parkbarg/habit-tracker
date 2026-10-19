# Alembic の autogenerate が全モデルを認識できるよう、ここで読み込む
from backend.models.goal import Goal
from backend.models.habit_record import HabitRecord

__all__ = ["Goal", "HabitRecord"]
