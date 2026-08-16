import uuid

from project_storage.models import User
from project_storage.project_access import ProjectAccess


class DeleteProjectUseCase:

    def __init__(self, project_access: ProjectAccess) -> None:
        self._project_access = project_access

    def delete(self, project_id: uuid.UUID, user: User) -> None:
        self._project_access.delete(user, project_id)
