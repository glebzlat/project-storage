import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from project_storage.repositories.participant_repository import (
    ParticipantRepository as ParticipantRepositoryProtocol,
    ParticipantExistsError,
    ParticipantNotFoundError
)
from project_storage.models import User, Project, ProjectParticipantAssociation


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

    def add(self, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
        if self.has_participant(project_id, user_id):
            raise ParticipantExistsError(
                "User already added to project",
                user_id=user_id,
                project_id=project_id
            )

        stmt_project = select(Project).where(Project.pid == project_id)
        stmt_user = select(User).where(User.uid == user_id)
        project = self._session.scalars(stmt_project).one()
        user = self._session.scalars(stmt_user).one()

        assoc = ProjectParticipantAssociation(
            project_id=project.id,
            user_id=user.id
        )

        self._session.add(assoc)

    def get_all(self, project_id: uuid.UUID) -> list[User]:
        stmt = (
            select(User)
            .join(ProjectParticipantAssociation)
            .join(Project)
            .where(Project.pid == project_id)
        )
        return list(self._session.scalars(stmt))

    def remove(self, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
        if not self.has_participant(project_id, user_id):
            raise ParticipantNotFoundError(
                "User is not a participant of project",
                user_id=user_id,
                project_id=project_id
            )

        stmt_project = select(Project).where(Project.pid == project_id)
        stmt_user = select(User).where(User.uid == user_id)
        project = self._session.scalars(stmt_project).one()
        user = self._session.scalars(stmt_user).one()

        assoc_stmt = select(ProjectParticipantAssociation).where(
            ProjectParticipantAssociation.project_id == project.id,
            ProjectParticipantAssociation.user_id == user.id
        )
        assoc = self._session.scalar(assoc_stmt)
        if assoc is not None:
            self._session.delete(assoc)
