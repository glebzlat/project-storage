from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from project_storage.use_cases.register_user import (
    RegisterUser,
    UsernameAlreadyTakenError
)
from project_storage.dependencies import (
    get_register_user_uc,
    get_authenticate_user_uc
)
from project_storage.schemas import Token


router = APIRouter()


@router.post("/register")
def register_user(
    user: RegisterUser,
    use_case=Depends(get_register_user_uc)
):
    try:
        result = use_case.execute(user)
        return result
    except UsernameAlreadyTakenError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )


@router.post("/token")
def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case=Depends(get_authenticate_user_uc)
):
    user = use_case.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = use_case.create_token(user)
    return Token(access_token=access_token, token_type="bearer")
