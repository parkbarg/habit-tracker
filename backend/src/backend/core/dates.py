import calendar


def days_in_month(year: int, month: int) -> int:
    """対象年月の日数を返す。"""
    _, days = calendar.monthrange(year, month)
    return days
