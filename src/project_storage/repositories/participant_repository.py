import uuid

from typing import Protocol

from project_storage.models import User


class ParticipantError(Exception):
    """Errors related to ParticipantRepository"""

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


class ParticipantRepository(Protocol):

    def has_participant(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Check whether the project has participant

        Returns:
            True if the project is in the participant list, False otherwise.
        """

    def add(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> None:
        """Add the user to the project as a participant

        Raises:
            ParticipantExistsError: If the project had this user as a
                participant prior to the call.
        """

    def get_all(
        self,
        project_id: uuid.UUID
    ) -> list[User]:
        """Get the list of users who has access to the project

        Returns:
            The list that includes all participants and the owner.
        """

    def remove(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> None:
        """Remove the user from project participants

        Raises:
            ParticipantNotFoundError: If the user is not a participant.
        """
