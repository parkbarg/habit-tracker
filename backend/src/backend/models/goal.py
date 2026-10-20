from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base

GOAL_NAME_MAX_LENGTH = 30


class Goal(Base):
    __tablename__ = "goals"
    # 大文字・小文字だけが異なる同名を拒否する
    __table_args__ = (
        Index("uq_goals_name_lower", text("lower(name)"), unique=True),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(GOAL_NAME_MAX_LENGTH))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
