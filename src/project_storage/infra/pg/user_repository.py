import uuid

from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from project_storage.models import User
from project_storage.repositories.user_repository import (
    UserRepository,
    UserExistsError
)
from project_storage.database import connect


class PgUserRepository(UserRepository):

    def get_by_id(self, id: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.uid == id)

        with connect() as session:
            return session.scalar(stmt)

    def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)

        with connect() as session:
            return session.scalar(stmt)

    def add(self, user: User) -> None:
        with connect() as session:
            session.add(user)
            try:
                session.commit()
                session.refresh(user)
            except IntegrityError:
                raise UserExistsError(
                    f"user with username={user.username} already exists"
                )
