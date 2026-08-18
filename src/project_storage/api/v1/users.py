from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from project_storage.dependencies.glue import UserServiceDependency
from project_storage.dependencies.authentication import get_current_user
from project_storage.services.user_service import (
    UsernameAlreadyTakenError,
    PasswordsDoNotMatchError
)
from project_storage.schemas.user import RegisterUser, RegisteredUser, Token
from project_storage.models import User


router = APIRouter()


@router.post("/register")
def register_user(
    user: RegisterUser,
    service: UserServiceDependency
):
    try:
        db_user = service.register(user)
        return RegisteredUser(
            id=db_user.uid,
            username=db_user.username
        )
    except UsernameAlreadyTakenError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )
    except PasswordsDoNotMatchError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided passwords don't match"
        )


@router.post("/token")
def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: UserServiceDependency
):
    user = service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = service.create_token(user)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me")
def read_me(current_user: Annotated[User, Depends(get_current_user)]):
    return {
        "id": current_user.uid,
        "username": current_user.username,
        "name": current_user.name
    }
