import uuid

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response

from project_storage.models import User
from project_storage.dependencies.glue import ParticipantServiceDependency
from project_storage.dependencies.authentication import get_current_user
from project_storage.dependencies.project_access import (
    Action,
    require_access
)
from project_storage.schemas.participant import (
    AddParticipant,
    Participant,
    ParticipantList
)
from project_storage.exceptions.user import UserNotFoundError
from project_storage.exceptions.participant import (
    ParticipantExistsError,
    ParticipantNotFoundError
)
from project_storage.exceptions.project import ProjectNotFoundError
from project_storage.error_model import ErrorModel


router = APIRouter()


@router.post(
    "/{project_id}/participants",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorModel,
            "description": "Project or user not found"
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorModel,
            "description": "Participant already added"
        }
    },
    response_model_exclude_unset=True
)
def invite_participant(
    project_id: uuid.UUID,
    participant: AddParticipant,
    current_user: Annotated[User, Depends(get_current_user)],
    service: ParticipantServiceDependency,
    access=Depends(require_access(Action.INVITE))
):
    try:
        service.add(project_id, participant.username)
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorModel.asjson(
                project_id=project_id,
                description="Project not found"
            )
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorModel.asjson(
                project_id=project_id,
                username=participant.username,
                description="User not found"
            )
        )
    except ParticipantExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ErrorModel.asjson(
                project_id=project_id,
                username=participant.username,
                description="Participant already added to the project"
            )
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{project_id}/participants",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorModel,
            "description": "Project not found"
        }
    },
    response_model_exclude_unset=True
)
def get_participants(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: ParticipantServiceDependency,
    access=Depends(require_access(Action.READ))
):
    participants = service.get_all(project_id)

    if participants is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorModel.asjson(
                project_id=project_id,
                description="Project not found"
            )
        )

    lst = ParticipantList(n=len(participants), participants=[])
    for p in participants:
        lst.participants.append(
            Participant(username=p.username, name=p.name, uid=p.uid)
        )
    return lst


@router.delete(
    "/{project_id}/participants/{participant_username}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorModel,
            "description": "Project, user or participant not found"
        }
    },
    response_model_exclude_unset=True
)
def remove_participant(
    project_id: uuid.UUID,
    participant_username: str,
    current_user: Annotated[User, Depends(get_current_user)],
    service: ParticipantServiceDependency,
    access=Depends(require_access(Action.DELETE))
):
    try:
        service.remove(project_id, participant_username)
    except ParticipantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorModel.asjson(
                project_id=project_id,
                username=participant_username,
                description="Participant not found on project"
            )
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorModel.asjson(
                project_id=project_id,
                description="Project not found"
            )
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorModel.asjson(
                project_id=project_id,
                username=participant_username,
                description="User not found"
            )
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
