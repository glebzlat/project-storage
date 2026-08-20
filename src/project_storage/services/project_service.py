import uuid

from typing import Optional

from project_storage.repositories.project_repository import ProjectRepository
from project_storage.repositories.user_repository import UserRepository
from project_storage.models import Project
from project_storage.schemas.project import UpdateProject
from project_storage.exceptions.project import ProjectNotFoundError


class ProjectService:

    def __init__(
        self,
        project_repository: ProjectRepository,
        user_repository: UserRepository
    ) -> None:
        self._project_repository = project_repository
        self._user_repository = user_repository

    def create(
        self,
        user_id: uuid.UUID,
        name: str,
        description: Optional[str]
    ) -> Project:
        user = self._user_repository.get_by_id(user_id)
        project = Project(
            pid=uuid.uuid4(),
            owner_id=user.id,
            name=name,
            description=description
        )
        return self._project_repository.create(user_id, project)

    def get(
        self,
        project_id: uuid.UUID
    ) -> Optional[Project]:
        try:
            return self._project_repository.get_by_id(project_id)
        except ProjectNotFoundError:
            return None

    def update(self, project_id: uuid.UUID, update: UpdateProject) -> None:
        values = update.model_dump(exclude_unset=True)
        self._project_repository.update(project_id, values)

    def delete(self, project_id: uuid.UUID) -> None:
        self._project_repository.delete(project_id)

    def get_all(self, user_id: uuid.UUID) -> list[Project]:
        return self._project_repository.get_all(user_id)
