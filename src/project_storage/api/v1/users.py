from fastapi import APIRouter, Depends, HTTPException, status

from project_storage.use_case import UseCase
from project_storage.use_cases.register_user import (
    RegisterUser,
    UsernameAlreadyTakenError
)
from project_storage.dependencies import get_register_user_uc


router = APIRouter()


@router.post("/register")
def register_user(
    user: RegisterUser,
    use_case: UseCase = Depends(get_register_user_uc)
):
    try:
        result = use_case.execute(user)
        return result
    except UsernameAlreadyTakenError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )
