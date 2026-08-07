from __future__ import annotations

import uuid

from sqlalchemy import String
from sqlalchemy.types import UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[uuid.UUID] = mapped_column(UUID())
    name: Mapped[str] = mapped_column(String(64))
    username: Mapped[str] = mapped_column(String(32), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(512))
