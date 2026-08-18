from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from project_storage.core.config import settings
from project_storage.models import User
from project_storage.dependencies.glue import get_user_service

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PATH}/users/token"
)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service=Depends(get_user_service)
) -> User:
    if (user := user_service.get_current(token)) is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
