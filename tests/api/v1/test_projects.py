import uuid
import pytest
import jwt

from datetime import timedelta, datetime, timezone
from unittest import mock

from fastapi import status

from project_storage.models import User
from project_storage.dependencies import (
    get_current_user_uc,
    get_create_project_uc
)
from project_storage.main import app
from project_storage.core.config import settings
from project_storage.models import Project


class CreateProjectUseCaseMock:

    def __init__(self, project):
        self.project = project

    def create(self, user, name: str, description: str):
        assert self.project.name == name
        assert self.project.description == description
        return self.project


@pytest.fixture()
def add_user():
    user = User(
        uid=uuid.uuid4(),
        username="johndoe",
        name="John Doe"
    )
    use_case_mock = mock.Mock()
    use_case_mock.get.return_value = user
    app.dependency_overrides[get_current_user_uc] = lambda: use_case_mock
    return user


@pytest.fixture()
def access_token(add_user):
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.JWT_EXPIRATION_TIME_MINUTES)
    jwt_data = {
        "sub": add_user.username,
        "name": add_user.name,
        "exp": expire,
        "iat": now
    }
    token = jwt.encode(
        jwt_data,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return token


@pytest.fixture()
def project():
    project = Project(
        pid=uuid.uuid4(),
        name="MyProject",
        description="My New Project"
    )
    use_case = CreateProjectUseCaseMock(project)
    app.dependency_overrides[get_create_project_uc] = lambda: use_case
    return project


def test_create_project_as_authenticated_user(
    test_client,
    access_token,
    project
):
    response = test_client.post(
        f"{settings.API_PATH}/projects/create",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": project.name, "description": project.description}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": str(project.pid), "name": project.name}
