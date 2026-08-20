import uuid

from typing import Protocol

from project_storage.models import User


class UserExistsError(Exception):
    """The user with the given username already exists."""


class UserNotFoundError(Exception):
    """User not found"""


class UserRepository(Protocol):

    def get_by_username(self, username: str) -> User:
        """Get the user by username

        Returns:
            User instance.

        Raises:
            UserNotFoundError: If the user with the given username is not
                found.
        """

    def get_by_id(self, id: uuid.UUID) -> User:
        """Get the user by id

        Returns:
            User instance.

        Raises:
            UserNotFoundError: If the user with the given id is not found.
        """

    def add(self, user: User) -> None:
        """Add a new user

        Raises:
            UserExistsError: If the user with the given username
                already exists.
        """
