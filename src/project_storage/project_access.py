import uuid

from typing import Optional

from project_storage.repositories.project_repository import (
    ProjectRepository,
    ProjectNotFoundError
)
from project_storage.models import User, Project


class AccessError(Exception):
    """User is not authorized to perform an action"""


class ProjectAccess:

    def __init__(
        self,
        project_repository: ProjectRepository,
        participant=False
    ) -> None:
        self._participant = participant
        self._project_repository = project_repository

    def get(self, user: User, id: uuid.UUID) -> Optional[Project]:
        project = self._project_repository.get_by_id(id)
        if project is None:
            return None
        self._check_roles(project, user)
        return project

    def delete(self, user: User, project_id: uuid.UUID) -> None:
        project = self._project_repository.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(
                f"project with id={project_id} not found for "
                f"the user with id={user.uid}"
            )
        self._check_roles(project, user)
        self._project_repository.delete(project.pid)

    def update(
        self,
        user: User,
        project_id: uuid.UUID,
        values: dict
    ) -> Project:
        project = self._project_repository.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(
                f"project with id={project_id} not found for "
                f"the user with id={user.uid}"
            )

        self._check_roles(project, user)
        self._project_repository.update(project.pid, values)
        return project

    def _check_roles(self, project: Project, user: User) -> None:
        if project.owner_id == user.id:
            return

        if (
            self._participant and
            self._project_repository.is_participant(user.uid, project.pid)
        ):
            return

        raise AccessError()
