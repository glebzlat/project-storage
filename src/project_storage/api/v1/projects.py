from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from project_storage.dependencies import (
    get_create_project_uc,
    get_current_user
)
from project_storage.schemas import CreateProject
from project_storage.models import User
from project_storage.repositories.project_repository import ProjectExistsError


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
    except ProjectExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project with specified name already exists"
        )
    return {
        "id": project.pid,
        "name": project.name
    }
