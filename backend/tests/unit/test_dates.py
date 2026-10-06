from datetime import date

from backend.core.dates import days_in_month, month_date_range


def test_days_in_month_returns_31_for_31_day_month():
    assert days_in_month(2026, 1) == 31


def test_days_in_month_returns_30_for_30_day_month():
    assert days_in_month(2026, 4) == 30


def test_days_in_month_returns_28_for_february_in_common_year():
    assert days_in_month(2026, 2) == 28


def test_days_in_month_returns_29_for_february_in_leap_year():
    assert days_in_month(2024, 2) == 29


def test_days_in_month_returns_28_for_february_in_century_non_leap_year():
    assert days_in_month(1900, 2) == 28


def test_days_in_month_returns_29_for_february_in_400_year_leap_year():
    assert days_in_month(2000, 2) == 29


def test_month_date_range_returns_first_and_last_day_of_month():
    assert month_date_range(2026, 10) == (date(2026, 10, 1), date(2026, 10, 31))


def test_month_date_range_returns_29th_as_last_day_of_february_in_leap_year():
    assert month_date_range(2024, 2) == (date(2024, 2, 1), date(2024, 2, 29))


def test_month_date_range_stays_within_same_year_for_december():
    assert month_date_range(2026, 12) == (date(2026, 12, 1), date(2026, 12, 31))
