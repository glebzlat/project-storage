import uuid
import jwt

from typing import Optional

from pydantic import BaseModel
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from project_storage.repositories.user_repository import UserRepository
from project_storage.core.config import settings


class CurrentUser(BaseModel):
    id: uuid.UUID
    username: str
    name: str


class CurrentUserUseCase:

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def get(self, token: str) -> Optional[CurrentUser]:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            if username := payload.get("sub"):
                if user := self._user_repository.get_by_username(username):
                    return CurrentUser(
                        id=user.uid,
                        username=user.username,
                        name=user.name
                    )
            return None
        except (InvalidTokenError, ExpiredSignatureError):
            return None
