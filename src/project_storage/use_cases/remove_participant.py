import uuid

from project_storage.project_access import ProjectAccess
from project_storage.models import User


class RemoveParticipantUseCase:

    def __init__(self, project_access: ProjectAccess) -> None:
        self._project_access = project_access

    def remove(
        self,
        user: User,
        project_id: uuid.UUID,
        username: str
    ) -> None:
        self._project_access.remove_participant(user, project_id, username)
