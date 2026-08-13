import uuid

import pytest

from project_storage.models import User
from project_storage.repositories.project_repository import ProjectRepository
from project_storage.use_cases.delete_project import (
    DeleteProjectUseCase,
    ProjectNotFound
)


class ProjectRepositoryFake(ProjectRepository):

    def __init__(self, raises_not_found=False):
        self.delete_call = None
        self.raises_not_found = raises_not_found

    def create(self, user, project):
        raise NotImplementedError

    def get_owned_by_name(self, user, name):
        raise NotImplementedError

    def get_by_id(self, id):
        raise NotImplementedError

    def update(self, user, project_id, values):
        raise NotImplementedError

    def delete(self, user, project_id):
        if self.raises_not_found:
            raise ProjectNotFound()
        self.delete_call = (user, project_id)


def make_user(id=1):
    return User(
        id=id,
        uid=uuid.uuid4(),
        username="johndoe",
        name="John Doe"
    )


def test_delete_project_delegates_to_repository():
    user = make_user()
    project_id = uuid.uuid4()
    repo = ProjectRepositoryFake()
    use_case = DeleteProjectUseCase(repo)

    result = use_case.delete(project_id, user)

    assert result is None
    deleted_user, deleted_project_id = repo.delete_call
    assert deleted_user is user
    assert deleted_project_id == project_id


def test_delete_project_propagates_not_found():
    user = make_user()
    project_id = uuid.uuid4()
    repo = ProjectRepositoryFake(raises_not_found=True)
    use_case = DeleteProjectUseCase(repo)

    with pytest.raises(ProjectNotFound):
        use_case.delete(project_id, user)
