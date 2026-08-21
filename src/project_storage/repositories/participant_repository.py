import uuid

from typing import Protocol

from project_storage.models import User


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
