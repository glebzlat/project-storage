import uuid


class ParticipantError(Exception):
    """Errors related to Participants"""

    def __init__(
        self,
        message: str,
        user_id: uuid.UUID,
        project_id: uuid.UUID
    ):
        super().__init__(message)
        self.user_id = user_id
        self.project_id = project_id


class ParticipantExistsError(ParticipantError):
    """Participant with the given username already added to the project"""


class ParticipantNotFoundError(ParticipantError):
    """Participant with the given username not found on the project"""

