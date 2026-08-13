import uuid

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response

from project_storage.dependencies import (
    get_create_project_uc,
    get_current_user,
    get_get_project_uc,
    get_update_project_uc,
    get_delete_project_uc
)
from project_storage.schemas import (
    CreateProject,
    UpdateProject,
    ExistingProject
)
from project_storage.models import User
from project_storage.repositories.project_repository import (
    ProjectExistsError,
    ProjectNotFoundError
)


router = APIRouter()


@router.post("/create")
def create_project(
    create_project: CreateProject,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case=Depends(get_create_project_uc)
):
    try:
        project = use_case.create(
            current_user,
            create_project.name,
            create_project.description
        )
        return ExistingProject(
            id=project.pid,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
            owner_id=current_user.uid
        )
    except ProjectExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project with specified name already exists"
        )


@router.get("/{project_id}")
def get_project(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case=Depends(get_get_project_uc)
):
    project = use_case.get(current_user, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return ExistingProject(
        id=project.pid,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        owner_id=current_user.uid
    )


@router.patch("/{project_id}")
def update_project(
    project_id: uuid.UUID,
    update_project: UpdateProject,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case=Depends(get_update_project_uc)
):
    try:
        use_case.update(project_id, current_user, update_project)
    except ProjectExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project with specified name already exists"
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{project_id}")
def delete_project(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case=Depends(get_delete_project_uc)
):
    try:
        use_case.delete(project_id, current_user)
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
