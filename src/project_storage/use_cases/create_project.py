from typing import Optional

from project_storage.models import User, Project
from project_storage.repositories.project_repository import ProjectRepository


class CreateProjectUseCase:

    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    def create(
        self,
        user: User,
        name: str,
        description: Optional[str]
    ) -> Project:
        p = Project(
            name=name,
            description=description
        )
        self._project_repository.create(user, p)
        return p
