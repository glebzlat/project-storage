import uuid

from pydantic import BaseModel
from pwdlib import PasswordHash

from project_storage.use_case import UseCase
from project_storage.repositories.user_repository import UserRepository
from project_storage.models import User
from project_storage.repositories.user_repository import UserExistsError


class RegisterUser(BaseModel):
    username: str
    name: str
    password: str


class RegisteredUser(BaseModel):
    id: uuid.UUID
    username: str


class UsernameAlreadyTakenError(Exception):
    """The user with the given username already exists."""


class RegisterUserUseCase(UseCase):

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def execute(self, request: RegisterUser) -> RegisteredUser:
        password_hash = PasswordHash.recommended()
        hashed_password = password_hash.hash(request.password)

        u = User(
            uid=uuid.uuid4(),
            username=request.username,
            name=request.name,
            hashed_password=hashed_password
        )

        try:
            self._user_repository.add(u)
            return RegisteredUser(id=u.uid, username=u.username)
        except UserExistsError:
            raise UsernameAlreadyTakenError(request.username)
