"""Unit tests for the activity-streak calculation."""
from datetime import date, timedelta

from app.services.stats_service import current_streak, _round_pct

T = date(2026, 6, 7)


def test_no_activity():
    assert current_streak([], today=T) == 0


def test_streak_ending_today():
    days = [T, T - timedelta(days=1), T - timedelta(days=2)]
    assert current_streak(days, today=T) == 3


def test_grace_for_yesterday():
    # studied yesterday + before, not yet today -> streak still counts
    days = [T - timedelta(days=1), T - timedelta(days=2)]
    assert current_streak(days, today=T) == 2


def test_broken_streak():
    days = [T, T - timedelta(days=2), T - timedelta(days=3)]  # gap at day-1
    assert current_streak(days, today=T) == 1


def test_stale_streak_is_zero():
    days = [T - timedelta(days=5)]
    assert current_streak(days, today=T) == 0


def test_round_pct():
    assert _round_pct(1, 4) == 25.0
    assert _round_pct(0, 0) == 0.0
