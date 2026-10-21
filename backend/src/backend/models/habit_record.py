from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    SmallInteger,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.enums import Status
from backend.db.base import Base

# Status Enumの値だけを許可する（例: "status IN (1, 2, 3)"）
STATUS_CHECK_SQL = f"status IN ({', '.join(str(s.value) for s in Status)})"


class HabitRecord(Base):
    __tablename__ = "habit_records"
    # 1目標・1日につき1記録だけにする
    __table_args__ = (
        UniqueConstraint(
            "goal_id", "record_date", name="uq_habit_records_goal_id_record_date"
        ),
        CheckConstraint(STATUS_CHECK_SQL, name="ck_habit_records_status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    goal_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("goals.id"))
    record_date: Mapped[date] = mapped_column(Date)
    # 値は core.enums.Status（1=SUCCESS, 2=PARTIAL, 3=FAILURE）
    status: Mapped[int] = mapped_column(SmallInteger)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
