from datetime import datetime

from fastapi import status

from sqlalchemy import select

from project_storage.core.config import settings
from project_storage.database import connect
from project_storage.models import Project


def test_create_project_as_authenticated_user(
    test_client,
    create_user,
    make_token,
):
    project_name, project_description = "MyProject", "My Awesome Project"
    user = create_user()
    token = make_token(user.username, user.name)

    response = test_client.post(
        f"{settings.API_PATH}/projects/create",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": project_name, "description": project_description}
    )

    with connect() as session:
        project = session.scalar(
            select(Project).where(Project.owner_id == user.id)
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(project.pid)
    assert data["name"] == project.name
    assert data["description"] == project.description
    assert data["owner_id"] == str(user.uid)
    assert (
        datetime.fromisoformat(data["created_at"]) == project.created_at
    )


def test_create_project_duplicate_project_name_returns_409(
    test_client,
    create_user,
    make_token
):
    project_name = "MyProject"
    user = create_user()
    token = make_token(user.username, user.name)

    response1 = test_client.post(
        f"{settings.API_PATH}/projects/create",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": project_name, "description": "My Awesome Project"}
    )
    response2 = test_client.post(
        f"{settings.API_PATH}/projects/create",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": project_name, "description": "My Super Project"}
    )

    assert response1.status_code == status.HTTP_200_OK
    assert response2.status_code == status.HTTP_409_CONFLICT
    assert response2.json() == {
        "detail": "Project with specified name already exists"
    }


def test_create_project_with_same_name_as_another_user(
    test_client,
    create_user,
    make_token
):
    project_name = "MyProject"
    user1 = create_user(username="johndoe", name="John")
    user2 = create_user(username="janedoe", name="Jane")
    token1 = make_token(user1.username, user1.name)
    token2 = make_token(user2.username, user2.name)

    response1 = test_client.post(
        f"{settings.API_PATH}/projects/create",
        headers={"Authorization": f"Bearer {token1}"},
        json={"name": project_name, "description": "My Awesome Project"}
    )
    response2 = test_client.post(
        f"{settings.API_PATH}/projects/create",
        headers={"Authorization": f"Bearer {token2}"},
        json={"name": project_name, "description": "My Awesome Project"}
    )

    def prepare_stmt(for_user):
        return select(Project).where(Project.owner_id == for_user.id)

    with connect() as session:
        project1 = session.scalar(prepare_stmt(user1))
        project2 = session.scalar(prepare_stmt(user2))

    assert response1.status_code == status.HTTP_200_OK
    assert response2.status_code == status.HTTP_200_OK
    assert project1.owner_id != project2.owner_id


def test_create_project_with_no_description(
    test_client,
    create_user,
    make_token
):
    user = create_user()
    token = make_token(user.username, user.name)

    response = test_client.post(
        f"{settings.API_PATH}/projects/create",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Project"}
    )

    with connect() as session:
        project = session.scalar(
            select(Project).where(Project.owner_id == user.id)
        )

    assert response.status_code == status.HTTP_200_OK
    assert project.description is None
