import uuid

from sqlalchemy import select, union_all
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload, Session

from project_storage.repositories.project_repository import (
    ProjectRepository as ProjectRepositoryProtocol,
    ProjectExistsError,
    ProjectNotFoundError
)
from project_storage.models import User, Project, ProjectParticipantAssociation


class ProjectRepository(ProjectRepositoryProtocol):

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, user_id: uuid.UUID, project: Project) -> Project:
        self._session.add(project)
        try:
            self._session.flush()
        except IntegrityError as e:
            self._session.rollback()
            raise ProjectExistsError(
                f"user with id={user_id} already has a project "
                f"named={project.name!r}"
            ) from e
        self._session.refresh(project)
        return project

    def get_by_id(self, project_id: uuid.UUID) -> Project:
        stmt = (
            select(Project)
            .where(Project.pid == project_id)
            .options(joinedload(Project.owner))
        )
        project = self._session.scalar(stmt)
        if project is None:
            raise ProjectNotFoundError()
        return project

    def update(
        self,
        project_id: uuid.UUID,
        values: dict
    ) -> None:
        stmt = select(Project).where(Project.pid == project_id)
        project = self._session.scalar(stmt)
        if project is None:
            raise ProjectNotFoundError(f"project {project_id} not found")
        for field, value in values.items():
            setattr(project, field, value)
        try:
            self._session.flush()
        except IntegrityError as e:
            self._session.rollback()
            raise ProjectExistsError(
                f"user already has a project named={values.get('name')!r}"
            ) from e
        self._session.refresh(project)

    def get_all(self, user_id: uuid.UUID) -> list[Project]:
        stmt_owner = (
            select(Project)
            .join(User)
            .where(User.uid == user_id)
        )
        stmt_participant = (
            select(Project)
            .join(ProjectParticipantAssociation)
            .join(User)
            .where(User.uid == user_id)
        )

        stmt_union = (
            union_all(stmt_owner, stmt_participant)
            .order_by(Project.id)
        )
        orm_stmt = (
            select(Project)
            .from_statement(stmt_union)
            .options(selectinload(Project.owner))
        )
        return list(self._session.scalars(orm_stmt))

    def delete(self, project_id: uuid.UUID) -> None:
        stmt = select(Project).where(Project.pid == project_id)
        project = self._session.scalar(stmt)
        if project is None:
            raise ProjectNotFoundError(f"project {project_id} not found")
        self._session.delete(project)
