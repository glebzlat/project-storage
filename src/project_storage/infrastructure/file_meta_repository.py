import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from project_storage.repositories.file_meta_repository import (
    FileMetaRepository as FileMetaRepositoryProtocol,
    DocumentExistsError,
    DocumentNotFoundError,
)
from project_storage.models import Project, User, FileMeta


class FileMetaRepository(FileMetaRepositoryProtocol):

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        file_meta: FileMeta
    ) -> FileMeta:
        stmt_project = select(Project).where(Project.pid == project_id)
        project = self._session.scalars(stmt_project).one()

        stmt_user = select(User).where(User.uid == user_id)
        user = self._session.scalars(stmt_user).one()

        file_meta.fid = uuid.uuid4()
        file_meta.project_id = project.id
        file_meta.uploaded_by_id = user.id

        self._session.add(file_meta)
        try:
            self._session.flush()
        except IntegrityError as e:
            self._session.rollback()
            raise DocumentExistsError(
                "File already exists on the project",
                filename=file_meta.filename,
                project_id=project_id
            ) from e
        self._session.refresh(file_meta)
        return file_meta

    def get_by_filename(self, project_id: uuid.UUID, filename: str) -> FileMeta:
        stmt_project = select(Project).where(Project.pid == project_id)
        project = self._session.scalars(stmt_project).one()

        stmt_file_meta = select(FileMeta).where(
            FileMeta.project_id == project.id,
            FileMeta.filename == filename,
        )
        file_meta = self._session.scalar(stmt_file_meta)
        if file_meta is None:
            raise DocumentNotFoundError(
                "File not found on the project",
                filename=filename,
                project_id=project_id,
            )
        return file_meta

    def get_by_id(self, file_id: uuid.UUID) -> FileMeta:
        stmt = select(FileMeta).where(FileMeta.fid == file_id)
        file_meta = self._session.scalar(stmt)
        if file_meta is None:
            raise DocumentNotFoundError("File not found", file_id=file_id,)
        return file_meta

    def get(self, file_id: uuid.UUID, project_id: uuid.UUID) -> FileMeta:
        stmt_project = select(Project).where(Project.pid == project_id)
        project = self._session.scalars(stmt_project).one()

        stmt_file_meta = (
            select(FileMeta)
            .where(FileMeta.fid == file_id, FileMeta.project_id == project.id)
        )
        file_meta = self._session.scalar(stmt_file_meta)
        if file_meta is None:
            raise DocumentNotFoundError(
                "File not found on the project",
                file_id=file_id,
                project_id=project_id
            )
        return file_meta

    def list(self, project_id: uuid.UUID) -> list[FileMeta]:
        stmt_project = select(Project).where(Project.pid == project_id)
        project = self._session.scalars(stmt_project).one()

        stmt_file_meta = (
            select(FileMeta)
            .where(FileMeta.project_id == project.id)
        )
        return list(self._session.scalars(stmt_file_meta))
