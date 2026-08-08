import pytest

from fastapi.testclient import TestClient

from project_storage.main import app


@pytest.fixture
def test_client():
    app.dependency_overrides.clear()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
