import asyncio
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def client():
    """Fixture for FastAPI TestClient."""
    return TestClient(app)


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-wide event loop for pytest-asyncio."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_session():
    """
    Fixture to mock an AsyncSession with execute, add, commit, refresh,
    and delete methods.
    """
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def sample_group_data():
    """Sample data dict for creating/updating a Group."""
    return {"name": "Test Group", "type": "group1"}


@pytest.fixture
def sample_site_data():
    """Sample data dict for creating/updating a Site."""
    return {
        "name": "Test Site",
        "country": "FR",
        "installation_date": "2025-07-01",
        "max_power_megawatt": 10.0,
        "min_power_megawatt": 5.0,
        "group_ids": [],
    }
