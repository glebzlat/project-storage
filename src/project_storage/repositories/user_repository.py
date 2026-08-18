import uuid

from typing import Protocol

from project_storage.models import User


class UserExistsError(Exception):
    """The user with the given username already exists."""


class UserNotFoundError(Exception):
    """User not found"""


class UserRepository(Protocol):

    def get_by_username(self, username: str) -> User:
        ...

    def get_by_id(self, id: uuid.UUID) -> User:
        ...

    def add(self, user: User) -> None:
        ...
