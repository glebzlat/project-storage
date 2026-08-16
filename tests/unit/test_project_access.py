import uuid
import pytest

from unittest import mock

from project_storage.models import User, Project
from project_storage.project_access import ProjectAccess, AccessError
from project_storage.repositories.project_repository import ProjectNotFoundError


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


def test_get_by_owner():
    user = make_user(id=1)
    project = make_project(user)

    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    access = ProjectAccess(repo_mock)

    p = access.get(user, project.pid)

    assert p is project
    repo_mock.get_by_id.assert_called_once_with(project.pid)


def test_get_project_not_found():
    user = make_user()

    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = None
    access = ProjectAccess(repo_mock)

    p = access.get(user, uuid.uuid4())
    assert p is None


def test_get_by_participant():
    owner = make_user(id=1)
    user = make_user(id=2)
    project = make_project(owner)

    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    repo_mock.is_participant.return_value = True  # Is a participant
    access = ProjectAccess(repo_mock, participant=True)

    p = access.get(user, project.pid)

    assert p is project
    repo_mock.get_by_id.assert_called_once_with(project.pid)
    repo_mock.is_participant.assert_called_once_with(user.uid, project.pid)


def test_get_by_participant_no_access_raises():
    owner = make_user(id=1)
    user = make_user(id=2)
    project = make_project(owner)

    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    repo_mock.is_participant.return_value = False  # Is not a participant
    access = ProjectAccess(repo_mock, participant=True)

    with pytest.raises(AccessError):
        access.get(user, project.pid)
    repo_mock.get_by_id.assert_called_once_with(project.pid)


def test_delete_by_owner():
    user = make_user()
    project = make_project(user)

    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    access = ProjectAccess(repo_mock)

    access.delete(user, project.pid)

    repo_mock.get_by_id.assert_called_once_with(project.pid)
    repo_mock.delete.assert_called_once_with(project.pid)


def test_delete_nonexistent_project_raises():
    user = make_user()

    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = None
    access = ProjectAccess(repo_mock)

    with pytest.raises(ProjectNotFoundError):
        access.delete(user, uuid.uuid4())


def test_delete_by_participant_raises():
    owner = make_user(id=1)
    user = make_user(id=2)
    project = make_project(owner)

    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    repo_mock.is_participant.return_value = True
    access = ProjectAccess(repo_mock)  # participant=False

    with pytest.raises(AccessError):
        access.delete(user, project.pid)

    repo_mock.get_by_id.assert_called_once_with(project.pid)


def test_update_by_owner():
    user = make_user(id=1)
    project = make_project(user)

    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    access = ProjectAccess(repo_mock)

    values = {"name": "New Name"}
    updated_project = access.update(user, project.pid, values)

    assert updated_project is project
    repo_mock.get_by_id.assert_called_once_with(project.pid)
    repo_mock.update.assert_called_once_with(project.pid, values)


def test_update_nonexistent_project_raises():
    user = make_user(id=1)

    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = None
    access = ProjectAccess(repo_mock)

    values = {"name": "New Name"}

    with pytest.raises(ProjectNotFoundError):
        access.update(user, uuid.uuid4(), values)


def test_update_by_participant():
    owner = make_user(id=1)
    user = make_user(id=2)
    project = make_project(owner)

    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    repo_mock.is_participant.return_value = True  # A participant
    access = ProjectAccess(repo_mock, participant=True)

    values = {"name": "New Name"}
    updated_project = access.update(user, project.pid, values)

    assert updated_project is project
    repo_mock.get_by_id.assert_called_once_with(project.pid)
    repo_mock.update.assert_called_once_with(project.pid, values)
    repo_mock.is_participant.assert_called_once_with(user.uid, project.pid)


def test_update_by_non_participant_raises():
    owner = make_user(id=1)
    user = make_user(id=2)
    project = make_project(owner)

    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    repo_mock.is_participant.return_value = False  # Not a participant
    access = ProjectAccess(repo_mock, participant=True)

    values = {"name": "New Name"}

    with pytest.raises(AccessError):
        access.update(user, project.pid, values)

    repo_mock.get_by_id.assert_called_once_with(project.pid)
    repo_mock.is_participant.assert_called_once_with(user.uid, project.pid)
