import uuid

from project_storage.repositories.participant_repository import (
    ParticipantRepository
)
from project_storage.repositories.user_repository import UserRepository
from project_storage.models import User


class ParticipantService:

    def __init__(
        self,
        participant_repository: ParticipantRepository,
        user_repository: UserRepository
    ) -> None:
        self._participant_repository = participant_repository
        self._user_repository = user_repository

    def add(
        self,
        project_id: uuid.UUID,
        invited_username: str
    ) -> None:
        user = self._user_repository.get_by_username(invited_username)
        self._participant_repository.add(project_id, user.uid)

    def remove(
        self,
        project_id: uuid.UUID,
        removed_username: str
    ) -> None:
        user = self._user_repository.get_by_username(removed_username)
        self._participant_repository.remove(project_id, user.uid)

    def get_all(
        self,
        project_id: uuid.UUID
    ) -> list[User]:
        return self._participant_repository.get_all(project_id)
