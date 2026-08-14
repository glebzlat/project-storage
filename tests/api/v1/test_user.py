import uuid

from http import HTTPStatus

from sqlalchemy import select

from project_storage.core.config import settings
from project_storage.database import connect
from project_storage.models import User


def test_register_user(test_client):
    response = test_client.post(
        f"{settings.API_PATH}/users/register",
        json={
            "username": "alice",
            "name": "Alice Doe",
            "password": "password123",
            "repeat_password": "password123"}
    )

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert uuid.UUID(body["id"])
    assert body["username"] == "alice"

    with connect() as session:
        user = session.scalar(select(User).where(User.username == "alice"))

    assert user is not None
    assert user.uid == uuid.UUID(body["id"])
    assert user.name == "Alice Doe"
    assert user.username == "alice"
    assert user.hashed_password != "password123"


def test_register_user_duplicate_returns_409(test_client, create_user):
    create_user(username="user")

    response = test_client.post(
        f"{settings.API_PATH}/users/register",
        json={
            "username": "user",
            "name": "John Doe",
            "password": "password123",
            "repeat_password": "password123"
        }
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": "Username already taken"}


def test_login_user(test_client, create_user, make_token):
    password = "alice123"
    user = create_user(username="alice", name="Alice", password=password)
    expected_jwt = make_token(user.username, user.name)

    response = test_client.post(
        f"{settings.API_PATH}/users/token",
        data={"username": user.username, "password": password}
    )

    response_data = response.json()

    assert response_data["token_type"] == "bearer"
    assert response_data["access_token"] == expected_jwt

    expected_jwt_data = jwt.decode(
        expected_jwt,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
    returned_jwt_data = jwt.decode(
        response_data["access_token"],
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )

    assert expected_jwt_data["sub"] == returned_jwt_data["sub"]
    assert expected_jwt_data["name"] == returned_jwt_data["name"]

    def fromtimestamp(ts):
        return datetime.fromtimestamp(ts, timezone.utc)

    expected_iat = fromtimestamp(expected_jwt_data["iat"])
    returned_iat = fromtimestamp(returned_jwt_data["iat"])
    assert abs(expected_iat - returned_iat) < timedelta(seconds=1)

    expected_exp = fromtimestamp(expected_jwt_data["exp"])
    returned_exp = fromtimestamp(returned_jwt_data["exp"])
    assert abs(expected_exp - returned_exp) < timedelta(seconds=1)


def test_login_nonexistent_user_returns_401(test_client, mocker):
    response = test_client.post(
        f"{settings.API_PATH}/users/token",
        data={"username": "johndoe", "password": "password123"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.headers.get("WWW-Authenticate") == "Bearer"
    assert response.json() == {"detail": "Incorrect username or password"}


def test_read_current_user(test_client, create_user, make_token):
    user = create_user()
    token = make_token(user.username, user.name)

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


def test_read_current_user_not_found_returns_401(test_client, make_token):
    token = make_token("benbitdiddle", "Ben Bitdiddle")

    response = test_client.get(
        f"{settings.API_PATH}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.headers.get("WWW-Authenticate") == "Bearer"
    assert response.json() == {"detail": "Could not validate credentials"}


def test_read_current_user_expired_token_returns_401(
    test_client,
    create_user,
    make_token
):
    # The user is created, so that this test cannot fail due to the
    # "user not found"
    create_user(username="johndoe")
    token = make_token("johndoe", "John Doe", expired=True)

    response = test_client.get(
        f"{settings.API_PATH}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.headers.get("WWW-Authenticate") == "Bearer"
    assert response.json() == {"detail": "Could not validate credentials"}
