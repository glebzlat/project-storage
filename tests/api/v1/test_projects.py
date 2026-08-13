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
