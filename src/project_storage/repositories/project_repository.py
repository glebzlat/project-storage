import uuid

from typing import Protocol, Optional

from project_storage.models import User, Project


class ProjectExistsError(Exception):
    """Project with the given name already exists"""


class ProjectRepository(Protocol):

    def create(self, user: User, project: Project) -> None:
        ...

    def get_owned_by_name(self, user: User, name: str) -> Optional[Project]:
        ...

    def get_by_id(self, id: uuid.UUID) -> Optional[Project]:
        ...

    def update(
        self,
        user: User,
        project_id: uuid.UUID,
        values: dict
    ) -> Optional[Project]:
        ...
