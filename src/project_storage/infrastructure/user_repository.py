import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from project_storage.models import User
from project_storage.repositories.user_repository import (
    UserRepository as UserRepositoryProtocol,
    UserExistsError,
    UserNotFoundError
)


class UserRepository(UserRepositoryProtocol):

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, id: uuid.UUID) -> User:
        stmt = select(User).where(User.uid == id)
        user = self._session.scalar(stmt)
        if user is None:
            raise UserNotFoundError()
        return user

    def get_by_username(self, username: str) -> User:
        stmt = select(User).where(User.username == username)
        user = self._session.scalar(stmt)
        if user is None:
            raise UserNotFoundError()
        return user

    def add(self, user: User) -> None:
        self._session.add(user)
        try:
            self._session.flush()
            self._session.refresh(user)
        except IntegrityError:
            self._session.rollback()
            raise UserExistsError(
                f"user with username={user.username} already exists"
            )
