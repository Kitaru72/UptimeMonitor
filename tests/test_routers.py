import pytest
from fastapi.testclient import TestClient
from types import SimpleNamespace
from datetime import datetime, timezone, timedelta

from app.main import app
from app.database import get_async_db
from app.models.check import CheckModel
from app.models.monitor import MonitorModel


FAKE_MONITORS = [
    SimpleNamespace(
        id=1,
        url="https://google.com",
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        is_active=True,
        last_checked_at=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
    ),
    SimpleNamespace(
        id=5,  # не 2! специально ломаем порядок
        url="https://github.com",
        created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
        is_active=True,
        last_checked_at=None,
    ),
    SimpleNamespace(
        id=3,
        url="https://stackoverflow.com",
        created_at=datetime(2024, 1, 3, tzinfo=timezone.utc),
        is_active=False,
        last_checked_at=datetime(2024, 1, 14, 9, 0, tzinfo=timezone.utc),
    ),
    SimpleNamespace(
        id=2,
        url="https://python.org",
        created_at=datetime(2024, 1, 4, tzinfo=timezone.utc),
        is_active=True,
        last_checked_at=datetime(2024, 1, 15, 11, 0, tzinfo=timezone.utc),
    ),
    SimpleNamespace(
        id=4,
        url="https://reddit.com",
        created_at=datetime(2024, 1, 5, tzinfo=timezone.utc),
        is_active=False,
        last_checked_at=None,
    ),
]

FAKE_CHECKS = [
    SimpleNamespace(
        id=1,
        monitor_id=1,
        status="UP",
        http_status_code=200,
        error_type=None,
        duration_ms=150,
        checked_at=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
    ),
    SimpleNamespace(
        id=2,
        monitor_id=1,
        status="UP",
        http_status_code=200,
        error_type=None,
        duration_ms=145,
        checked_at=datetime(2024, 1, 15, 9, 0, tzinfo=timezone.utc),
    ),
    SimpleNamespace(
        id=3,
        monitor_id=1,
        status="DOWN",
        http_status_code=500,
        error_type=None,
        duration_ms=2000,
        checked_at=datetime(2024, 1, 15, 8, 0, tzinfo=timezone.utc),
    ),
    SimpleNamespace(
        id=4,
        monitor_id=2,  # другой монитор!
        status="UP",
        http_status_code=200,
        error_type=None,
        duration_ms=80,
        checked_at=datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc),
    ),
    SimpleNamespace(
        id=5,
        monitor_id=1,
        status="DOWN",
        http_status_code=None,
        error_type="TIMEOUT",
        duration_ms=5000,
        checked_at=datetime(2024, 1, 15, 7, 0, tzinfo=timezone.utc),
    ),
]


@pytest.fixture
def client():
    async def get_fake_db():
        yield FakeDb(monitors=FAKE_MONITORS, checks=FAKE_CHECKS)

    app.dependency_overrides[get_async_db] = get_fake_db
    yield TestClient(app)
    app.dependency_overrides.clear()

class FakeScalarsResult:
    def __init__(self, items):
        self.items = items

    def all(self):
        return self.items


class FakeDb:
    def __init__(self, monitors=None, checks=None):
        self.monitors = monitors or []
        self.checks = checks or []

    async def scalar(self, statement):
        query = str(statement)
        if "FROM monitors" in query:
            return len(self.monitors)
        if "FROM checks" in query:
            return len(self.checks)

    async def scalars(self, statement):
        query = str(statement)
        
        if "FROM monitors" in query:
            return FakeScalarsResult(self.monitors)
        
        if "FROM checks" in query:
            items = self.checks
            # Если есть WHERE monitor_id — фильтруем (для тестов всегда id=1)
            if "WHERE checks.monitor_id" in query:
                items = [c for c in items if c.monitor_id == 1]
            return FakeScalarsResult(items)
        
        return FakeScalarsResult([])
                

    async def get(self, model, id):
        if model is MonitorModel:
            for m in self.monitors:
                if m.id == id:
                    return m
        if model is CheckModel:
            for c in self.checks:
                if c.id == id:
                    return c



def test_get_monitors_returns_paginated_response(client):
    response = client.get("/monitors")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert data["limit"] == 20
    assert data["offset"] == 0


def test_get_monitors_with_limits(client):
    response = client.get("/monitors?limit=2&offset=1")
    assert response.status_code == 200
    data = response.json()
    assert data["offset"] == 1
    assert data["limit"] == 2


def test_get_monitors_invalid_limit_returns_422(client):
    response = client.get("/monitors?limit=0")
    assert response.status_code == 422


def test_get_checks_returns_paginated_response(client):
    response = client.get("/monitors/1/checks")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_get_checks_for_noexistance_monitor_returns_404(client):
    response = client.get("/monitors/999/checks")
    assert response.status_code == 404

def test_get_checks_filters_by_monitor_id(client):
    response = client.get("/monitors/1/checks")
    data = response.json()
    
    for item in data["items"]:
        assert item["monitor_id"] == 1
    
    assert len(data["items"]) == 4


@pytest.fixture
def client_with_pagination():
    """Клиент, который возвращает только 2 монитора (как будто LIMIT сработал)"""
    async def get_fake_db():
        yield FakeDb(monitors=FAKE_MONITORS[1:3])  # offset=1, limit=2
    
    app.dependency_overrides[get_async_db] = get_fake_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_get_monitors_pagination_works(client_with_pagination):
    response = client_with_pagination.get("/monitors?limit=2&offset=1")
    data = response.json()
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 1