import uuid

from typing import Optional

from project_storage.models import User, Project
from project_storage.project_access import ProjectAccess


class GetProjectUseCase:

    def __init__(self, project_access: ProjectAccess) -> None:
        self._project_access = project_access

    def get(self, user: User, project_id: uuid.UUID) -> Optional[Project]:
        return self._project_access.get(user, project_id)
