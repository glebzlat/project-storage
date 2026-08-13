from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from project_storage.use_cases.register_user import RegisterUserUseCase
from project_storage.use_cases.authenticate_user import AuthenticateUserUseCase
from project_storage.use_cases.current_user import CurrentUserUseCase
from project_storage.use_cases.create_project import CreateProjectUseCase
from project_storage.use_cases.get_project import GetProjectUseCase
from project_storage.use_cases.update_project import UpdateProjectUseCase
from project_storage.infra.pg.user_repository import PgUserRepository
from project_storage.infra.pg.project_repository import PgProjectRepository
from project_storage.core.config import settings
from project_storage.models import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PATH}/users/token"
)


def get_register_user_uc():
    return RegisterUserUseCase(get_user_repository())


def get_authenticate_user_uc():
    return AuthenticateUserUseCase(get_user_repository())


def get_current_user_uc():
    return CurrentUserUseCase(get_user_repository())


def get_create_project_uc():
    return CreateProjectUseCase(get_project_repository())


def get_get_project_uc():
    return GetProjectUseCase(get_user_repository(), get_project_repository())


def get_update_project_uc():
    return UpdateProjectUseCase(get_project_repository())


def get_user_repository():
    return PgUserRepository()


def get_project_repository():
    return PgProjectRepository()


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    use_case=Depends(get_current_user_uc)
) -> User:
    if (user := use_case.get(token)) is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
