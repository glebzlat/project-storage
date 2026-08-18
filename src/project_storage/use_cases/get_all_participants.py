import uuid

from project_storage.project_access import ProjectAccess
from project_storage.models import User


class GetAllParticipantsUseCase:

    def __init__(self, project_access: ProjectAccess) -> None:
        self._project_access = project_access

    def get(self, user: User, project_id: uuid.UUID) -> list[User]:
        return self._project_access.get_participants(user, project_id)
