from datetime import date

import pytest
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
