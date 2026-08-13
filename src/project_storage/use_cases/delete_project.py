import uuid

from project_storage.models import User
from project_storage.repositories.project_repository import ProjectRepository


class DeleteProjectUseCase:

    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    def delete(self, project_id: uuid.UUID, user: User) -> None:
        self._project_repository.delete(user, project_id)
