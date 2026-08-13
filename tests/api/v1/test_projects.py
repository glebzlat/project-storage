import uuid

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


def test_get_project(
    test_client,
    create_user,
    create_project,
    make_token
):
    user = create_user()
    project = create_project(user.id)
    token = make_token(user.username, user.name)

    response = test_client.get(
        f"{settings.API_PATH}/projects/{project.pid}",
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == str(project.pid)
    assert data["name"] == project.name
    assert data["description"] == project.description
    assert datetime.fromisoformat(data["created_at"]) == project.created_at
    assert data["owner_id"] == str(user.uid)


def test_get_non_existing_project_returns_404(
    test_client,
    create_user,
    make_token
):
    user = create_user()
    token = make_token(user.username, user.name)

    response = test_client.get(
        f"{settings.API_PATH}/projects/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project not found"}


def test_get_project_of_another_user_returns_404(
    test_client,
    create_user,
    create_project,
    make_token
):
    project_name = "MyUniqueProject"
    user1, user2 = create_user(), create_user()
    _, project2 = (
        create_project(user1.id, name=project_name),
        create_project(user2.id, name=project_name)
    )
    token1 = make_token(user1.username, user1.name)

    response = test_client.get(
        f"{settings.API_PATH}/projects/{project2.pid}",
        headers={"Authorization": f"Bearer {token1}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_project(
    test_client,
    create_user,
    create_project,
    make_token
):
    user = create_user()
    project = create_project(
        user.id, name="MyAwesomeProject", description="Description1"
    )
    token = make_token(user.username, user.name)

    response = test_client.patch(
        f"{settings.API_PATH}/projects/{project.pid}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "MySuperProject", "description": "Description2"}
    )

    with connect() as session:
        db_project = session.scalar(
            select(Project).where(Project.owner_id == user.id)
        )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db_project.name == "MySuperProject"
    assert db_project.description == "Description2"


def test_update_project_set_description_to_none(
    test_client,
    create_user,
    create_project,
    make_token
):
    user = create_user()
    project = create_project(
        user.id, name="MyAwesomeProject", description="Description1"
    )
    token = make_token(user.username, user.name)

    response = test_client.patch(
        f"{settings.API_PATH}/projects/{project.pid}",
        headers={"Authorization": f"Bearer {token}"},
        json={"description": None}
    )

    with connect() as session:
        db_project = session.scalar(
            select(Project).where(Project.owner_id == user.id)
        )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db_project.name == project.name
    assert db_project.description is None


def test_update_project_unchanged(
    test_client,
    create_user,
    create_project,
    make_token
):
    user = create_user()
    project = create_project(
        user.id, name="MyAwesomeProject", description="Description1"
    )
    token = make_token(user.username, user.name)

    response = test_client.patch(
        f"{settings.API_PATH}/projects/{project.pid}",
        headers={"Authorization": f"Bearer {token}"},
        json={}
    )

    with connect() as session:
        db_project = session.scalar(
            select(Project).where(Project.owner_id == user.id)
        )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db_project.name == project.name
    assert db_project.description == project.description


def test_update_project_rename_to_existing_name_returns_409(
    test_client,
    create_user,
    create_project,
    make_token
):
    user = create_user()
    project1 = create_project(user.id, name="project1")
    project2 = create_project(user.id, name="project2")
    token = make_token(user.username, user.name)

    response = test_client.patch(
        f"{settings.API_PATH}/projects/{project2.pid}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": project1.name}
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": "Project with specified name already exists"
    }


def test_update_project_nonexisting_project_returns_404(
    test_client,
    create_user,
    create_project,
    make_token
):
    user1, user2 = create_user(), create_user()
    project1 = create_project(user1.id, name="project")
    token = make_token(user2.username, user2.name)

    response = test_client.patch(
        f"{settings.API_PATH}/projects/{project1.pid}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "AnotherName"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project not found"}
