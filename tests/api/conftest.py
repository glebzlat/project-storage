import uuid
import pytest
import jwt
import boto3

from pathlib import Path
from typing import Optional
from datetime import timedelta, datetime, timezone

from alembic import command
from alembic.config import Config as AlembicConfig

from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import text

from fastapi.testclient import TestClient

from pwdlib import PasswordHash

from botocore.exceptions import ClientError

from project_storage.main import app
from project_storage.database import _engine, connect
from project_storage.models import Base, User, Project, ProjectParticipantAssociation
from project_storage.core.config import settings


@pytest.fixture(scope="session", autouse=True)
def apply_alembic_migrations(pytestconfig):
    DB_URL = settings.DB_URL

    if not database_exists(DB_URL):
        create_database(DB_URL)

    rootdir = Path(pytestconfig.rootdir)
    alembic_ini = rootdir / "alembic.ini"

    cfg = AlembicConfig(str(alembic_ini))
    cfg.set_main_option("sqlalchemy.url", DB_URL)

    command.upgrade(cfg, "head")
    yield


@pytest.fixture(autouse=True)
def truncate_tables():
    yield

    tables = ", ".join(
        f'"{t.name}"' for t in reversed(Base.metadata.sorted_tables)
    )
    if not tables:
        return

    with _engine.begin() as con:
        con.execute(
            text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE")
        )


@pytest.fixture
def test_client():
    app.dependency_overrides.clear()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def create_user():

    def _create(
        uid: Optional[uuid.UUID] = None,
        username: Optional[str] = None,
        name="John Doe",
        password="password123"
    ) -> User:
        if uid is None:
            uid = uuid.uuid4()

        if username is None:
            username = f"user_{uuid.uuid4().hex[:8]}"

        ph = PasswordHash.recommended()
        hashed_pwd = ph.hash(password)

        u = User(
            uid=uid,
            username=username,
            name=name,
            hashed_password=hashed_pwd
        )

        with connect() as session:
            session.add(u)
            session.commit()
            session.refresh(u)

        return u

    return _create


@pytest.fixture
def create_project():

    def _create(user_db_id: int, name=None, description=None):
        if name is None:
            name = f"Project{uuid.uuid4().hex[:8]}"

        p = Project(
            pid=uuid.uuid4(),
            name=name,
            description=description,
            owner_id=user_db_id
        )

        with connect() as session:
            session.add(p)
            session.commit()
            session.refresh(p)

        return p

    return _create


@pytest.fixture
def add_participant():

    def _add(project: Project, user: User) -> None:
        assoc = ProjectParticipantAssociation(
            project_id=project.id,
            user_id=user.id
        )
        with connect() as session:
            session.add(assoc)
            session.commit()

    return _add


@pytest.fixture
def make_token():

    def _make(
        username="johndoe",
        name="John Doe",
        expired=False
    ) -> str:
        now = datetime.now(timezone.utc)
        if expired:
            # Set now to the past
            minutes = settings.JWT_EXPIRATION_TIME_MINUTES + 1
            now = now - timedelta(minutes=minutes)
        expire = now + timedelta(minutes=settings.JWT_EXPIRATION_TIME_MINUTES)
        payload = {
            "sub": username,
            "name": name,
            "exp": expire,
            "iat": now
        }
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    return _make


@pytest.fixture
def s3_file_exists():

    def _exists(key):
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.AWS_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        try:
            s3.head_object(Bucket=settings.AWS_S3_BUCKET_NAME, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    return _exists
