import uuid

from typing import Protocol, Optional

from project_storage.models import User


class UserExistsError(Exception):
    """The user with the given username already exists."""


class UserNotFoundError(Exception):
    """User with the given username not found"""


class UserRepository(Protocol):

    def get_by_username(self, username: str) -> Optional[User]:
        ...

    def get_by_id(self, id: uuid.UUID) -> Optional[User]:
        ...

    def add(self, user: User) -> None:
        ...
