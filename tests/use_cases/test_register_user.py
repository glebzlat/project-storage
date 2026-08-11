import pytest

from pwdlib import PasswordHash

from project_storage.repositories.user_repository import (
    UserRepository,
    UserExistsError
)
from project_storage.models import User
from project_storage.use_cases.register_user import (
    RegisterUser,
    UsernameAlreadyTakenError,
    RegisterUserUseCase,
    PasswordsDoNotMatchError
)


class UserRepositoryFake(UserRepository):

    def __init__(self):
        self.users: list[User] = []

    def get_by_id(self, id):
        raise NotImplementedError

    def get_by_username(self, username):
        raise NotImplementedError

    def add(self, user: User) -> None:
        if any(u.username == user.username for u in self.users):
            raise UserExistsError()
        self.users.append(user)


def test_register_user_adds_to_repo_and_returns_response():
    repo = UserRepositoryFake()
    use_case = RegisterUserUseCase(repo)
    register_request = RegisterUser(
        username="user",
        name="John Doe",
        password="password123",
        repeat_password="password123"
    )
    password_hash = PasswordHash.recommended()

    result = use_case.execute(register_request)

    assert result.id is not None
    assert result.username == "user"
    assert len(repo.users) == 1

    added_user = repo.users[0]
    assert added_user.name == register_request.name
    assert added_user.username == register_request.username
    assert added_user.uid == result.id
    assert password_hash.verify(
        register_request.password,
        added_user.hashed_password
    )


def test_register_user_duplicate_user_raises_already_taken_error():
    repo = UserRepositoryFake()
    use_case = RegisterUserUseCase(repo)
    register_request = RegisterUser(
        username="johndoe",
        name="John Doe",
        password="password123",
        repeat_password="password123"
    )

    use_case.execute(register_request)

    with pytest.raises(UsernameAlreadyTakenError, match="^johndoe$"):
        use_case.execute(register_request)


def test_register_user_password_mismatch_raises_error():
    repo = UserRepositoryFake()
    use_case = RegisterUserUseCase(repo)
    register_request = RegisterUser(
        username="johndoe",
        name="John Doe",
        password="password123",
        repeat_password="password234"
    )

    with pytest.raises(PasswordsDoNotMatchError):
        use_case.execute(register_request)
