import uuid

from typing import Optional


class UserError(Exception):
    """Errors related to user functionality"""

    def __init__(
        self,
        username: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> None:
        super().__init__()
        self.username = username
        self.user_id = user_id


class UserExistsError(UserError):
    """User already exists"""


class UserNotFoundError(UserError):
    """User not found"""


class UserPasswordError(UserError):
    """Passwords do not match"""
