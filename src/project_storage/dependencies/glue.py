from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from project_storage.services.user_service import UserService
from project_storage.services.project_service import ProjectService
from project_storage.services.participant_service import (
    ParticipantService
)
from project_storage.infrastructure.user_repository import UserRepository
from project_storage.infrastructure.project_repository import ProjectRepository
from project_storage.infrastructure.participant_repository import (
    ParticipantRepository
)
from project_storage.database import create_session


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


def get_session(
    session: Annotated[Session, Depends(create_session)]
) -> Session:
    return session


UserServiceDependency = Annotated[UserService, Depends(get_user_service)]
ProjectServiceDependency = Annotated[
    ProjectService, Depends(get_project_service)
]
ParticipantServiceDependency = Annotated[
    ParticipantService, Depends(get_participant_service)
]
