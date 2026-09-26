from datetime import datetime, timedelta

import pytest

from types import SimpleNamespace

from app.services.monitor_activity import should_pause_monitor


CURRENT_TIME = datetime(2026, 9, 26, 15, 30)


@pytest.mark.parametrize(
    ("is_active", "created_at_delta", "expected"),
    [
        (True, timedelta(days=1, hours=2), True),
        (False, timedelta(days=1, hours=2), False),
    ],
)
def test_should_pause_monitor_based_on_activity_and_created_at(
    is_active, created_at_delta, expected
):
    monitor = SimpleNamespace(
        is_active=is_active,
        created_at=CURRENT_TIME - created_at_delta,
        last_checked_at=None,
    )
    assert should_pause_monitor(monitor, CURRENT_TIME) == expected


def test_does_not_pause_recently_checked_active_monitor():
    monitor = SimpleNamespace(
        created_at=CURRENT_TIME - timedelta(days=10),
        is_active=True,
        last_checked_at=CURRENT_TIME - timedelta(hours=2),
    )

    result = should_pause_monitor(monitor, CURRENT_TIME)

    assert result is False


def test_should_pause_monitor_checked_exactly_one_day_ago():
    monitor = SimpleNamespace(
        is_active=True, last_checked_at=CURRENT_TIME - timedelta(days=1)
    )

    result = should_pause_monitor(monitor, CURRENT_TIME)

    assert result is True
