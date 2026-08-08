import jwt
import pytest

from unittest import mock
from datetime import timedelta, datetime, timezone

from pwdlib import PasswordHash

from project_storage.use_cases.authenticate_user import AuthenticateUserUseCase
from project_storage.models import User
from project_storage.core.config import settings


@pytest.mark.parametrize(
    "db_username,db_password,username,password,user_found",
    [
        ("johndoe", "password123", "johndoe", "password123", True),
        ("johndoa", "password123", "johndoe", "password123", False),
        ("johndoe", "password124", "johndoe", "password123", False)
    ]
)
def test_authenticate_user(
    db_username, db_password, username, password, user_found
):
    ph = PasswordHash.recommended()
    repo_mock = mock.Mock()
    repo_mock.get_by_username.side_effect = lambda usrname: (
        User(username=db_username, hashed_password=ph.hash(db_password))
        if usrname == db_username
        else None
    )
    use_case = AuthenticateUserUseCase(repo_mock)

    authenticated_user = use_case.authenticate(username, password)

    if user_found:
        assert user_found and authenticated_user is not None
        assert authenticated_user.username == username
        assert ph.verify(password, authenticated_user.hashed_password)
    else:
        assert not user_found and authenticated_user is None


def test_create_token():
    repo_mock = mock.Mock()
    user = User(username="johndoe", name="John Doe")
    repo_mock.get_by_username.return_value = user
    use_case = AuthenticateUserUseCase(repo_mock)

    now = datetime.now(timezone.utc)
    expected_expire = now + timedelta(minutes=settings.JWT_EXPIRATION_TIME_MINUTES)

    token = use_case.create_token(user)

    token_data = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )

    assert token_data["sub"] == user.username
    assert token_data["name"] == user.name
    assert token_data["exp"] == int(expected_expire.timestamp())
    assert token_data["iat"] == int(now.timestamp())
