import uuid

from typing import Optional

from project_storage.models import User, Project
from project_storage.repositories.project_repository import ProjectRepository
from project_storage.repositories.user_repository import UserRepository
from project_storage.schemas import UpdateProject


class UpdateProjectUseCase:

    def __init__(
        self,
        user_repository: UserRepository,
        project_repository: ProjectRepository
    ) -> None:
        self._user_repository = user_repository
        self._project_repository = project_repository

    def update(
        self,
        project_id: uuid.UUID,
        user: User,
        update_project: UpdateProject
    ) -> Optional[Project]:
        db_user = self._user_repository.get_by_id(user.uid)
        if db_user is None:
            return None

        values = update_project.model_dump(exclude_unset=True)
        return self._project_repository.update(db_user, project_id, values)
