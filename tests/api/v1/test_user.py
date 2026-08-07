import uuid
import pytest

from unittest import mock
from http import HTTPStatus

from fastapi.testclient import TestClient

from project_storage.main import app
from project_storage.core.config import settings
from project_storage.dependencies import get_register_user_uc
from project_storage.use_cases.register_user import (
    RegisteredUser,
    UsernameAlreadyTakenError
)


@pytest.fixture
def test_client():
    app.dependency_overrides.clear()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_register_user(test_client):

    uid = uuid.uuid4()
    use_case_mock = mock.Mock()
    use_case_mock.execute.return_value = RegisteredUser(id=uid, username="user")
    app.dependency_overrides[get_register_user_uc] = lambda: use_case_mock

    response = test_client.post(
        f"{settings.API_PATH}/users/register",
        json={"username": "user", "name": "John Doe", "password": "password123"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": str(uid),
        "username": "user",
    }
    use_case_mock.execute.assert_called_once()


def test_register_user_duplicate_returns_409(test_client):
    use_case_mock = mock.Mock()
    use_case_mock.execute.side_effect = UsernameAlreadyTakenError("user")
    app.dependency_overrides[get_register_user_uc] = lambda: use_case_mock

    response = test_client.post(
        f"{settings.API_PATH}/users/register",
        json={"username": "user", "name": "John Doe", "password": "password123"}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": "Username already taken"}
    use_case_mock.execute.assert_called_once()
