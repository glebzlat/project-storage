import uuid

from project_storage.models import User, Project
from project_storage.repositories.project_repository import ProjectRepository
from project_storage.use_cases.get_all_projects import GetAllProjectsUseCase


class ProjectRepositoryFake(ProjectRepository):

    def __init__(self, projects):
        self.projects = projects
        self.get_all_call = None

    def create(self, user, project):
        raise NotImplementedError

    def get_owned_by_name(self, user, name):
        raise NotImplementedError

    def get_by_id(self, id):
        raise NotImplementedError

    def update(self, user, project_id, values):
        raise NotImplementedError

    def get_all(self, user):
        self.get_all_call = user
        return self.projects


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


def test_get_all_projects_returns_projects_for_user():
    user = make_user()
    projects = [make_project(user) for _ in range(3)]
    use_case = GetAllProjectsUseCase(ProjectRepositoryFake(projects))

    result = use_case.get(user)

    assert result == projects
    assert use_case._project_repository.get_all_call is user


def test_get_all_projects_returns_empty_list_when_none():
    user = make_user()
    use_case = GetAllProjectsUseCase(ProjectRepositoryFake([]))

    result = use_case.get(user)

    assert result == []
    assert use_case._project_repository.get_all_call is user
