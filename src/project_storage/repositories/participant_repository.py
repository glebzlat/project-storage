import uuid

from typing import Protocol


class ParticipantRepository(Protocol):

    def has_participant(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        ...
