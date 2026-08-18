import uuid

from project_storage.project_access import ProjectAccess


class AddParticipantUseCase:

    def __init__(self, project_access: ProjectAccess) -> None:
        self._project_access = project_access

    def add(
        self,
        project_id: uuid.UUID,
        issuer_id: uuid.UUID,
        username: str
    ) -> None:
        self._project_access.add_participant(project_id, issuer_id, username)
