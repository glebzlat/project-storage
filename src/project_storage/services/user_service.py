import uuid
import logging
import jwt

from typing import Optional
from datetime import timedelta, datetime, timezone

from pwdlib import PasswordHash
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from project_storage.repositories.user_repository import (
    UserRepository,
    UserExistsError,
    UserNotFoundError
)
from project_storage.models import User
from project_storage.schemas.user import RegisterUser
from project_storage.core.config import settings


class UsernameAlreadyTakenError(Exception):
    """The user with the given username already exists."""

    def __init__(self, message: str, username: str) -> None:
        super().__init__(message)
        self.username = username


class PasswordsDoNotMatchError(Exception):
    """Password does not match repeated password."""


class UserService:

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def authenticate(self, username: str, password: str) -> Optional[User]:
        try:
            user = self._user_repository.get_by_username(username)
        except UserNotFoundError:
            logging.error("authenticate: user not found")
            return None

        ph = PasswordHash.recommended()
        if not ph.verify(password, user.hashed_password):
            logging.error("authenticate: incorrect password")
            return None
        return user

    def create_token(self, user: User) -> str:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=settings.JWT_EXPIRATION_TIME_MINUTES)
        data = {
            "sub": user.username,
            "name": user.name,
            "exp": expire,
            "iat": now
        }
        return jwt.encode(
            data,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    def register(self, request: RegisterUser) -> User:
        if request.password != request.repeat_password:
            raise PasswordsDoNotMatchError("Passwords do not match")

        ph = PasswordHash.recommended()
        hashed_password = ph.hash(request.password)

        user = User(
            uid=uuid.uuid4(),
            username=request.username,
            name=request.name,
            hashed_password=hashed_password
        )

        try:
            self._user_repository.add(user)
            return user
        except UserExistsError:
            raise UsernameAlreadyTakenError(
                "Username already taken",
                request.username
            )

    def get_current(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            if username := payload.get("sub"):
                if user := self._user_repository.get_by_username(username):
                    return user
            return None
        except (InvalidTokenError, ExpiredSignatureError, UserNotFoundError):
            return None
