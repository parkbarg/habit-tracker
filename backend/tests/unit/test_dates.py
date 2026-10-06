from backend.core.dates import days_in_month


def test_days_in_month_returns_31_for_31_day_month():
    assert days_in_month(2026, 1) == 31


def test_days_in_month_returns_30_for_30_day_month():
    assert days_in_month(2026, 4) == 30
