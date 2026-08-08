import jwt

from typing import Optional
from datetime import timedelta, datetime, timezone

from pwdlib import PasswordHash

from project_storage.repositories.user_repository import UserRepository
from project_storage.models import User
from project_storage.core.config import settings


class AuthenticateUserUseCase:

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self._user_repository.get_by_username(username)
        if not user:
            return None
        password_hash = PasswordHash.recommended()
        if not password_hash.verify(password, user.hashed_password):
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
