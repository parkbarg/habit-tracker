from enum import IntEnum


class Status(IntEnum):
    """習慣記録のステータス。値はDBの habit_records.status と一致させる。"""

    SUCCESS = 1
    PARTIAL = 2
    FAILURE = 3
