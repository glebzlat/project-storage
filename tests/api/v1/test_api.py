import pytest

from http import HTTPStatus

from fastapi.testclient import TestClient

from project_storage.main import app


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


def test_api_root(test_client):
    response = test_client.get("/api/healthcheck")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "The API is alive"}
