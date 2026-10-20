import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models import Goal


def test_goal_name_unique_ignores_case(db_session: Session) -> None:
    db_session.add(Goal(name="abc"))
    db_session.commit()

    db_session.add(Goal(name="ABC"))
    with pytest.raises(IntegrityError, match="uq_goals_name_lower"):
        db_session.commit()
