from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from project_storage.use_cases.register_user import (
    RegisterUser,
    UsernameAlreadyTakenError
)
from project_storage.use_cases.current_user import CurrentUser
from project_storage.dependencies import (
    get_register_user_uc,
    get_authenticate_user_uc,
    get_current_user_uc
)
from project_storage.schemas import Token
from project_storage.core.config import settings


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PATH}/users/token"
)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    use_case=Depends(get_current_user_uc)
) -> CurrentUser:
    if (user := use_case.get(token)) is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )


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


@router.get("/me")
def read_me(current_user: Annotated[CurrentUser, Depends(get_current_user)]):
    return current_user
