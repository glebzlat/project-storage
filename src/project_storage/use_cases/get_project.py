import uuid

from typing import Optional

from project_storage.models import User, Project
from project_storage.repositories.project_repository import ProjectRepository
from project_storage.repositories.user_repository import UserRepository


class GetProjectUseCase:

    def __init__(
        self,
        user_repository: UserRepository,
        project_repository: ProjectRepository
    ) -> None:
        self._user_repository = user_repository
        self._project_repository = project_repository

    def get(
        self,
        user: User,
        project_id: uuid.UUID
    ) -> Optional[Project]:
        # Resolve the persisted user so the ownership check is made
        # against the user's internal id rather than the caller-provided
        # object, which may not be fully loaded from the database.
        db_user = self._user_repository.get_by_id(user.uid)
        if db_user is None:
            return None

        project = self._project_repository.get_by_id(project_id)
        if project is None or project.owner_id != db_user.id:
            return None
        return project
