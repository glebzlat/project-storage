import uuid

from typing import Protocol

from project_storage.models import Project


class ProjectExistsError(Exception):
    """Project with the given name already exists"""


class ProjectNotFoundError(Exception):
    """Project not found"""


class ProjectRepository(Protocol):

    def create(self, user_id: uuid.UUID, project: Project) -> Project:
        ...

    def get_by_id(self, project_id: uuid.UUID) -> Project:
        ...

    def update(
        self,
        project_id: uuid.UUID,
        values: dict
    ) -> None:
        ...

    def get_all(self, user_id: uuid.UUID) -> list[Project]:
        ...

    def delete(self, project_id: uuid.UUID) -> None:
        ...
