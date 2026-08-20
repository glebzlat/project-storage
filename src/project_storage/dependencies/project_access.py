import uuid

from enum import Enum
from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status

from project_storage.models import User
from project_storage.dependencies.glue import (
    get_project_repository,
    get_participant_repository
)
from project_storage.repositories.project_repository import (
    ProjectRepository,
    ProjectNotFoundError
)
from project_storage.repositories.participant_repository import (
    ParticipantRepository
)
from project_storage.dependencies.authentication import get_current_user


class AccessError(Exception):
    """User is not authorized to perform an action"""


class Role(str, Enum):
    OWNER = "owner"
    PARTICIPANT = "participant"


class Action(str, Enum):
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    INVITE = "invite"
    UPLOAD = "upload"


PROJECT_PERMISSIONS: dict[Role, set[Action]] = {
    Role.OWNER: {
        Action.READ,
        Action.UPDATE,
        Action.DELETE,
        Action.INVITE,
        Action.UPLOAD
    },
    Role.PARTICIPANT: {
        Action.READ,
        Action.UPDATE,
        Action.UPLOAD
    },
}


def get_project_role(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[
        ProjectRepository,
        Depends(get_project_repository)],
    participant_repo: Annotated[
        ParticipantRepository,
        Depends(get_participant_repository)]
) -> Role:
    try:
        project = project_repo.get_by_id(project_id)
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")

    if project.owner_id == current_user.id:
        return Role.OWNER

    if participant_repo.has_participant(project.pid, current_user.uid):
        return Role.PARTICIPANT

    raise HTTPException(
        status.HTTP_404_NOT_FOUND,
        detail="Project not found"
    )


def require_access_parametrize(
    action: Action, permissions: dict[Role, set[Action]]
) -> Callable[[Role], None]:
    def dependency(role: Role = Depends(get_project_role)) -> None:
        if action not in permissions[role]:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"{role.name} cannot {action.name}"
            )
    return dependency


def require_access(action: Action) -> Callable[[Role], None]:
    return require_access_parametrize(action, PROJECT_PERMISSIONS)
