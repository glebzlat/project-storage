from typing import List

from project_storage.models import User, Project
from project_storage.repositories.project_repository import ProjectRepository


class GetAllProjectsUseCase:

    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    def get(self, user: User) -> List[Project]:
        return self._project_repository.get_all(user)
