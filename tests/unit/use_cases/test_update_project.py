import uuid

from project_storage.models import User, Project
from project_storage.repositories.project_repository import ProjectRepository
from project_storage.schemas import UpdateProject
from project_storage.use_cases.update_project import UpdateProjectUseCase


class ProjectRepositoryFake(ProjectRepository):

    def __init__(self, project):
        self.project = project
        self.update_call = None

    def create(self, user, project):
        raise NotImplementedError

    def get_owned_by_name(self, user, name):
        raise NotImplementedError

    def get_by_id(self, id):
        raise NotImplementedError

    def update(self, user, project_id, values):
        self.update_call = (user, project_id, values)
        return self.project


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


def make_use_case(project):
    project_repo = ProjectRepositoryFake(project)
    use_case = UpdateProjectUseCase(project_repo)
    return use_case, project_repo


def test_update_project_applies_only_provided_fields():
    user = make_user()
    project = make_project(user)
    use_case, project_repo = make_use_case(project)

    result = use_case.update(
        project.pid,
        user,
        UpdateProject(name="MySuperProject")
    )

    assert result is project
    updated_user, project_id, values = project_repo.update_call
    assert updated_user is user
    assert project_id == project.pid
    assert values == {"name": "MySuperProject"}


def test_update_project_with_no_fields_passes_empty_values():
    user = make_user()
    project = make_project(user)
    use_case, project_repo = make_use_case(project)

    result = use_case.update(project.pid, user, UpdateProject())

    assert result is project
    assert project_repo.update_call[2] == {}


def test_update_project_explicit_none_clears_field():
    user = make_user()
    project = make_project(user)
    use_case, project_repo = make_use_case(project)

    result = use_case.update(
        project.pid,
        user,
        UpdateProject(description=None)
    )

    assert result is project
    assert project_repo.update_call[2] == {"description": None}


def test_update_project_returns_none_when_project_not_found():
    user = make_user()
    project_repo = ProjectRepositoryFake(None)
    use_case = UpdateProjectUseCase(project_repo)

    result = use_case.update(
        uuid.uuid4(),
        user,
        UpdateProject(name="MySuperProject")
    )

    assert result is None
    assert project_repo.update_call is not None
