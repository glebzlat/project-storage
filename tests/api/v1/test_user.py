import uuid
import jwt

from unittest import mock
from http import HTTPStatus
from datetime import timedelta, datetime, timezone

from project_storage.main import app
from project_storage.core.config import settings
from project_storage.dependencies import (
    get_register_user_uc,
    get_authenticate_user_uc,
    get_current_user_uc
)
from project_storage.use_cases.register_user import (
    RegisteredUser,
    UsernameAlreadyTakenError
)
from project_storage.use_cases.authenticate_user import AuthenticateUserUseCase
from project_storage.use_cases.current_user import CurrentUserUseCase
from project_storage.models import User


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


def test_login_user(test_client, mocker):
    password = "password123"
    user = User(username="johndoe", name="John Doe")
    repo_mock = mock.Mock()
    use_case = AuthenticateUserUseCase(repo_mock)
    mocker.patch.object(use_case, "authenticate", return_value=user)
    app.dependency_overrides[get_authenticate_user_uc] = lambda: use_case

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.JWT_EXPIRATION_TIME_MINUTES)
    jwt_data = {
        "sub": user.username,
        "name": user.name,
        "exp": expire,
        "iat": now
    }
    expected_jwt = jwt.encode(
        jwt_data,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    response = test_client.post(
        f"{settings.API_PATH}/users/token",
        data={"username": user.username, "password": password}
    )

    response_data = response.json()

    assert response_data["token_type"] == "bearer"
    assert response_data["access_token"] == expected_jwt


def test_login_nonexistent_user_returns_401(test_client, mocker):
    password = "password123"
    user = User(username="johndoe", name="John Doe")
    repo_mock = mock.Mock()
    use_case = AuthenticateUserUseCase(repo_mock)
    mocker.patch.object(use_case, "authenticate", return_value=None)
    app.dependency_overrides[get_authenticate_user_uc] = lambda: use_case

    response = test_client.post(
        f"{settings.API_PATH}/users/token",
        data={"username": user.username, "password": password}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.headers.get("WWW-Authenticate") == "Bearer"
    assert response.json() == {"detail": "Incorrect username or password"}


def test_read_current_user(test_client):
    user = User(
        uid=uuid.uuid4(),
        username="johndoe",
        name="John Doe"
    )
    repo_mock = mock.Mock()
    repo_mock.get_by_username.return_value = user
    use_case = CurrentUserUseCase(repo_mock)
    app.dependency_overrides[get_current_user_uc] = lambda: use_case

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.JWT_EXPIRATION_TIME_MINUTES)
    jwt_data = {
        "sub": user.username,
        "name": user.name,
        "exp": expire,
        "iat": now
    }
    token = jwt.encode(
        jwt_data,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    response = test_client.get(
        f"{settings.API_PATH}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": str(user.uid),
        "username": user.username,
        "name": user.name
    }


def test_read_current_user_not_found_returns_401(test_client):
    user = User(
        uid=uuid.uuid4(),
        username="johndoe",
        name="John Doe"
    )
    repo_mock = mock.Mock()
    repo_mock.get_by_username.return_value = None
    use_case = CurrentUserUseCase(repo_mock)
    app.dependency_overrides[get_current_user_uc] = lambda: use_case

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.JWT_EXPIRATION_TIME_MINUTES)
    jwt_data = {
        "sub": user.username,
        "name": user.name,
        "exp": expire,
        "iat": now
    }
    token = jwt.encode(
        jwt_data,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    response = test_client.get(
        f"{settings.API_PATH}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.headers.get("WWW-Authenticate") == "Bearer"
    assert response.json() == {"detail": "Could not validate credentials"}


def test_read_current_user_expired_token_returns_401(test_client):
    user = User(
        uid=uuid.uuid4(),
        username="johndoe",
        name="John Doe"
    )
    repo_mock = mock.Mock()
    repo_mock.get_by_username.return_value = user
    use_case = CurrentUserUseCase(repo_mock)
    app.dependency_overrides[get_current_user_uc] = lambda: use_case

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=-1)  # Set expire to the past
    jwt_data = {
        "sub": user.username,
        "name": user.name,
        "exp": expire,
        "iat": now
    }
    token = jwt.encode(
        jwt_data,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    response = test_client.get(
        f"{settings.API_PATH}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.headers.get("WWW-Authenticate") == "Bearer"
    assert response.json() == {"detail": "Could not validate credentials"}
