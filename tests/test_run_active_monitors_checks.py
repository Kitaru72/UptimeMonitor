from types import SimpleNamespace

import pytest

from app.models.monitor import MonitorModel
from app.services import batch_checker


class FakeScalarsResult:
    def __init__(self, monitors: list[MonitorModel]):
        self.monitors = monitors

    def all(self):
        return self.monitors


class FakeDb:
    def __init__(self, monitors: list):
        self.monitors = monitors
        self.added_checks = []
        self.commit_calls = 0

    async def scalars(self, statement):
        return FakeScalarsResult(self.monitors)

    def add(self, check):
        self.added_checks.append(check)

    async def commit(self):
        self.commit_calls += 1


@pytest.mark.anyio
async def test_run_active_monitors_checks_creates_checks_and_updates_monitors(monkeypatch):
    monitors = [
        SimpleNamespace(
            id=1,
            url="https://example.com",
            last_checked_at=None,
        ),
        SimpleNamespace(
            id=2,
            url="https://example1.com",
            last_checked_at=None,
        ),
    ]

    db = FakeDb(monitors)

    async def fake_check_urls(urls):
        return [
            {
                "status": "UP",
                "http_status_code": 200,
                "error_type": None,
                "duration_ms": 1134,
            },
            {
                "status": "DOWN",
                "http_status_code": None,
                "error_type": "CONNECTION_ERROR",
                "duration_ms": 4214,
            },
        ]

    monkeypatch.setattr(batch_checker, "check_urls", fake_check_urls)

    checks = await batch_checker.run_active_monitors_checks(db)

    assert len(checks) == 2
    assert len(db.added_checks) == 2
    assert db.commit_calls == 1

    assert checks[0].monitor_id == 1
    assert checks[0].status == "UP"
    assert checks[0].http_status_code == 200
    assert checks[0].error_type is None
    assert checks[0].duration_ms == 1134

    assert checks[1].monitor_id == 2
    assert checks[1].status == "DOWN"
    assert checks[1].http_status_code is None
    assert checks[1].error_type == "CONNECTION_ERROR"
    assert checks[1].duration_ms == 4214

    assert monitors[0].last_checked_at == checks[0].checked_at
    assert monitors[1].last_checked_at == checks[1].checked_at

    assert checks[0].checked_at == checks[1].checked_at