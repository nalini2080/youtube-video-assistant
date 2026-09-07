import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db


@pytest.fixture
def client():
    """
    A TestClient with the database dependency overridden. Deliberately NOT
    used as a context manager (no `with`) — that would trigger the app's
    real startup lifecycle (CREATE EXTENSION / create_all against Postgres),
    which we don't want for isolated, mock-only API tests.
    """
    async def fake_get_db():
        yield AsyncMock()

    app.dependency_overrides[get_db] = fake_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()