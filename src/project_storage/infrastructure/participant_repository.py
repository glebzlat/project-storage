import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from project_storage.models import Project, User, ProjectParticipantAssociation
from project_storage.repositories.participant_repository import (
    ParticipantRepository as ParticipantRepositoryProtocol
)


class ParticipantRepository(ParticipantRepositoryProtocol):

    def __init__(self, session: Session) -> None:
        self._session = session

    def has_participant(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        stmt = (
            select(ProjectParticipantAssociation)
            .join(
                Project,
                Project.id == ProjectParticipantAssociation.project_id
            )
            .join(User, User.id == ProjectParticipantAssociation.user_id)
            .where(Project.pid == project_id, User.uid == user_id)
        )
        return self._session.scalar(stmt) is not None
