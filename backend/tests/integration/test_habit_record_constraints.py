from datetime import date

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.enums import Status
from backend.models import Goal, HabitRecord


def test_habit_record_unique_per_goal_and_date(db_session: Session) -> None:
    goal = Goal(name="SC勉強")
    db_session.add(goal)
    db_session.commit()
    record_date = date(2026, 10, 1)

    db_session.add(
        HabitRecord(goal_id=goal.id, record_date=record_date, status=Status.SUCCESS)
    )
    db_session.commit()

    db_session.add(
        HabitRecord(goal_id=goal.id, record_date=record_date, status=Status.FAILURE)
    )
    with pytest.raises(IntegrityError, match="uq_habit_records_goal_id_record_date"):
        db_session.commit()


@pytest.mark.parametrize("invalid_status", [0, 4])
def test_habit_record_rejects_status_out_of_range(
    db_session: Session, invalid_status: int
) -> None:
    goal = Goal(name="SC勉強")
    db_session.add(goal)
    db_session.commit()

    db_session.add(
        HabitRecord(
            goal_id=goal.id, record_date=date(2026, 10, 1), status=invalid_status
        )
    )
    with pytest.raises(IntegrityError, match="ck_habit_records_status"):
        db_session.commit()


def test_deleting_goal_cascades_to_habit_records(db_session: Session) -> None:
    goal = Goal(name="SC勉強")
    other_goal = Goal(name="筋トレ")
    db_session.add_all([goal, other_goal])
    db_session.commit()
    db_session.add_all(
        [
            HabitRecord(
                goal_id=goal.id, record_date=date(2026, 10, 1), status=Status.SUCCESS
            ),
            HabitRecord(
                goal_id=goal.id, record_date=date(2026, 10, 2), status=Status.FAILURE
            ),
            HabitRecord(
                goal_id=other_goal.id,
                record_date=date(2026, 10, 1),
                status=Status.PARTIAL,
            ),
        ]
    )
    db_session.commit()

    # ORMのカスケードではなくDB制約を確認するため、SQLのDELETE文で直接削除する
    db_session.execute(delete(Goal).where(Goal.id == goal.id))
    db_session.commit()

    def count_records(goal_id: int) -> int:
        return db_session.scalar(
            select(func.count()).where(HabitRecord.goal_id == goal_id)
        )

    assert count_records(goal.id) == 0
    assert count_records(other_goal.id) == 1
