import uuid

from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from project_storage.repositories.project_repository import (
    ProjectRepository,
    ProjectExistsError
)
from project_storage.models import User, Project
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
        stmt = select(Project).where(Project.pid == id)

        with connect() as session:
            return session.scalar(stmt)
