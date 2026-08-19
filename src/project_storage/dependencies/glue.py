from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from project_storage.database import create_session
from project_storage.infrastructure.file_meta_repository import FileMetaRepository
from project_storage.infrastructure.file_repository import FileRepository
from project_storage.infrastructure.participant_repository import ParticipantRepository
from project_storage.infrastructure.project_repository import ProjectRepository
from project_storage.infrastructure.user_repository import UserRepository
from project_storage.persistence.file_storage import S3Client
from project_storage.services.file_service import FileService
from project_storage.services.participant_service import ParticipantService
from project_storage.services.project_service import ProjectService
from project_storage.services.user_service import UserService


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    return UserService(user_repository)


def get_project_service(
    project_repository: Annotated[
        ProjectRepository, Depends(get_project_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> ProjectService:
    return ProjectService(project_repository, user_repository)


def get_participant_service(
    participant_repository: Annotated[
        ParticipantRepository, Depends(get_participant_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> ParticipantService:
    return ParticipantService(participant_repository, user_repository)


def get_file_service(
    file_repository: Annotated[FileRepository, Depends(get_file_repository)],
    file_meta_repository: Annotated[
        FileMetaRepository, Depends(get_file_meta_repository)]
) -> FileService:
    return FileService(
        file_repository,
        file_meta_repository
    )


def get_user_repository(
    session: Annotated[Session, Depends(get_session)]
) -> UserRepository:
    return UserRepository(session)


def get_project_repository(
    session: Annotated[Session, Depends(get_session)]
) -> ProjectRepository:
    return ProjectRepository(session)


def get_participant_repository(
    session: Annotated[Session, Depends(get_session)]
) -> ParticipantRepository:
    return ParticipantRepository(session)


def get_file_repository(
    s3_client: Annotated[S3Client, Depends(get_s3_client)]
) -> FileRepository:
    return FileRepository(s3_client)


def get_file_meta_repository(
    session: Annotated[Session, Depends(get_session)]
) -> FileMetaRepository:
    return FileMetaRepository(session)


def get_s3_client() -> S3Client:
    return S3Client()


def get_session(
    session: Annotated[Session, Depends(create_session, scope="function")]
) -> Session:
    return session


UserServiceDependency = Annotated[UserService, Depends(get_user_service)]
ProjectServiceDependency = Annotated[
    ProjectService, Depends(get_project_service)
]
ParticipantServiceDependency = Annotated[
    ParticipantService, Depends(get_participant_service)
]
FileServiceDependency = Annotated[
    FileService, Depends(get_file_service)
]
