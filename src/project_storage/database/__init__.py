import logging

from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.project_storage.core.config import settings


_logger = logging.getLogger(__name__)

_engine = create_engine(settings.DB_URL)
SessionFactory = sessionmaker(autoflush=False, autocommit=False, bind=_engine)


def connect() -> Iterator[Session]:
    db = SessionFactory()
    try:
        yield db
    except Exception as e:
        _logger.error("Database error: %s", e)
        db.rollback()
        raise
    finally:
        db.close()
