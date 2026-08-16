import uuid

from typing import Optional

from project_storage.models import User, Project
from project_storage.project_access import ProjectAccess
from project_storage.schemas import UpdateProject


class UpdateProjectUseCase:

    def __init__(self, project_access: ProjectAccess) -> None:
        self._project_access = project_access

    def update(
        self,
        project_id: uuid.UUID,
        user: User,
        update_project: UpdateProject
    ) -> Optional[Project]:
        values = update_project.model_dump(exclude_unset=True)
        return self._project_access.update(user, project_id, values)
