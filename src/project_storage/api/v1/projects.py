import uuid

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response

from project_storage.dependencies.glue import ProjectServiceDependency
from project_storage.dependencies.authentication import get_current_user
from project_storage.dependencies.project_access import (
    Action,
    require_access
)
from project_storage.schemas.project import (
    CreateProject,
    UpdateProject,
    ExistingProject,
    ExistingProjectList
)
from project_storage.models import User
from project_storage.repositories.project_repository import (
    ProjectExistsError,
    ProjectNotFoundError
)
from project_storage.api.v1.participants import router as participants_router
from project_storage.api.v1.documents import router as documents_router


router = APIRouter()
router.include_router(participants_router)
router.include_router(documents_router, prefix="/{project_id}/documents")


@router.post("/create")
def create_project(
    create_project: CreateProject,
    current_user: Annotated[User, Depends(get_current_user)],
    service: ProjectServiceDependency
):
    try:
        project = service.create(
            current_user.uid,
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
    service: ProjectServiceDependency,
    access=Depends(require_access(Action.READ))
):
    project = service.get(project_id)
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
        owner_id=project.owner.uid
    )


@router.patch("/{project_id}")
def update_project(
    project_id: uuid.UUID,
    update_project: UpdateProject,
    current_user: Annotated[User, Depends(get_current_user)],
    service: ProjectServiceDependency,
    access=Depends(require_access(Action.UPDATE))
):
    try:
        service.update(project_id, update_project)
    except ProjectExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project with specified name already exists"
        )
    except (ProjectNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{project_id}")
def delete_project(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: ProjectServiceDependency,
    access=Depends(require_access(Action.DELETE))
):
    try:
        service.delete(project_id)
    except (ProjectNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("")
def get_all_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    service: ProjectServiceDependency
):
    projects = service.get_all(current_user.uid)
    lst = ExistingProjectList(n=len(projects), projects=[])
    for p in projects:
        schema = ExistingProject(
            id=p.pid,
            name=p.name,
            description=p.description,
            created_at=p.created_at,
            owner_id=p.owner.uid
        )
        lst.projects.append(schema)
    return lst
