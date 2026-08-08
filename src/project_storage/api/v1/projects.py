from typing import Annotated

from fastapi import APIRouter, Depends

from project_storage.dependencies import (
    get_create_project_uc,
    get_current_user
)
from project_storage.schemas import CreateProject
from project_storage.models import User


router = APIRouter()


@router.post("/create")
def create_project(
    create_project: CreateProject,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case=Depends(get_create_project_uc)
):
    project = use_case.create(
        current_user,
        create_project.name,
        create_project.description
    )
    return {
        "id": project.pid,
        "name": project.name
    }
