import calendar
from datetime import date

FIRST_DAY_OF_MONTH = 1


def days_in_month(year: int, month: int) -> int:
    """対象年月の日数を返す。"""
    _, days = calendar.monthrange(year, month)
    return days


def month_date_range(year: int, month: int) -> tuple[date, date]:
    """対象年月の初日と末日（両端を含む記録検索の範囲）を返す。"""
    first_day = date(year, month, FIRST_DAY_OF_MONTH)
    last_day = date(year, month, days_in_month(year, month))
    return first_day, last_day
