import uuid

from typing import Optional

from sqlalchemy import select, union_all
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from project_storage.repositories.project_repository import (
    ProjectRepository,
    ProjectExistsError
)
from project_storage.models import User, Project, ProjectParticipantAssociation
from project_storage.database import connect


class PgProjectRepository(ProjectRepository):

    def create(self, user: User, project: Project) -> None:
        project.pid = uuid.uuid4()
        project.owner_id = user.id

        with connect() as session:
            session.add(project)
            try:
                session.commit()
            except IntegrityError as e:
                raise ProjectExistsError(
                    f"user with id={user.uid} already has a project "
                    f"named={project.name!r}"
                ) from e
            else:
                session.refresh(project)

    def get_owned_by_name(self, user: User, name: str) -> Optional[Project]:
        stmt = (
            select(Project)
            .where(Project.owner_id == user.id, Project.name == name)
        )
        with connect() as session:
            return session.scalar(stmt)

    def get_by_id(self, id: uuid.UUID) -> Optional[Project]:
        stmt = (
            select(Project)
            .where(Project.pid == id)
            .options(joinedload(Project.owner))
        )

        with connect() as session:
            return session.scalar(stmt)

    def update(
        self,
        project_id: uuid.UUID,
        values: dict
    ) -> None:
        stmt = select(Project).where(Project.pid == project_id)
        with connect() as session:
            project = session.scalar(stmt)

            for field, value in values.items():
                setattr(project, field, value)

            try:
                session.commit()
            except IntegrityError as e:
                raise ProjectExistsError(
                    f"user already has a project named={values.get('name')!r}"
                ) from e
            else:
                session.refresh(project)

    def get_all(self, user: User) -> list[Project]:
        stmt_owner = (
            select(Project)
            .where(Project.owner_id == user.id)
        )
        stmt_participant = (
            select(Project)
            .join(ProjectParticipantAssociation)
            .join(User)
            .where(User.uid == user.uid)
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

        with connect() as session:
            return list(session.scalars(orm_stmt))

    def delete(self, project_id: uuid.UUID) -> None:
        stmt = select(Project).where(Project.pid == project_id)
        with connect() as session:
            project = session.scalar(stmt)
            session.delete(project)
            session.commit()

    def is_participant(
        self,
        user_id: uuid.UUID,
        project_id: uuid.UUID
    ) -> bool:
        stmt = (
            select(Project)
            .join(ProjectParticipantAssociation)
            .join(User)
            .where(User.uid == user_id, Project.pid == project_id)
        )

        with connect() as session:
            return session.scalar(stmt) is not None
