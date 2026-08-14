import uuid

from project_storage.models import User, Project
from project_storage.repositories.project_repository import ProjectRepository
from project_storage.repositories.user_repository import UserRepository
from project_storage.use_cases.get_project import GetProjectUseCase


class UserRepositoryFake(UserRepository):

    def __init__(self, user: User):
        self.user = user

    def get_by_username(self, username):
        raise NotImplementedError

    def add(self, user: User) -> None:
        raise NotImplementedError

    def get_by_id(self, id):
        return self.user if id == self.user.uid else None


class ProjectRepositoryFake(ProjectRepository):

    def __init__(self, projects):
        self.projects = projects

    def create(self, user, project):
        raise NotImplementedError

    def get_owned_by_name(self, user, name):
        raise NotImplementedError

    def get_by_id(self, id):
        return next(
            (p for p in self.projects if p.pid == id),
            None
        )


def make_user(id=1):
    return User(
        id=id,
        uid=uuid.uuid4(),
        username="johndoe",
        name="John Doe"
    )


def make_project(user):
    return Project(
        pid=uuid.uuid4(),
        name="MyProject",
        description="My New Project",
        owner_id=user.id
    )


def test_get_project_returns_project_owned_by_user():
    user = make_user()
    project = make_project(user)
    use_case = GetProjectUseCase(
        UserRepositoryFake(user),
        ProjectRepositoryFake([project])
    )

    result = use_case.get(user, project.pid)

    assert result is project


def test_get_project_returns_none_when_project_not_found():
    user = make_user()
    use_case = GetProjectUseCase(
        UserRepositoryFake(user),
        ProjectRepositoryFake([])
    )

    result = use_case.get(user, uuid.uuid4())

    assert result is None


def test_get_project_returns_none_when_owned_by_another_user():
    user = make_user(id=1)
    other_user = make_user(id=2)
    project = make_project(other_user)
    use_case = GetProjectUseCase(
        UserRepositoryFake(user),
        ProjectRepositoryFake([project])
    )

    result = use_case.get(user, project.pid)

    assert result is None
