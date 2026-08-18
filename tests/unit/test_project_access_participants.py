import uuid
import pytest

from unittest import mock

from project_storage.models import User, Project
from project_storage.project_access import ProjectAccess, AccessError
from project_storage.repositories.project_repository import (
    ProjectNotFoundError
)
from project_storage.repositories.user_repository import UserNotFoundError


def make_user(id=1, username="johndoe"):
    return User(
        id=id,
        uid=uuid.uuid4(),
        username=username,
        name="John Doe"
    )


def make_project(user):
    return Project(
        pid=uuid.uuid4(),
        name="MyProject",
        description="My New Project",
        owner_id=user.id
    )


def test_get_participants_by_owner():
    owner = make_user(id=1)
    participant = make_user(id=2, username="jane")
    project = make_project(owner)

    user_repo_mock = mock.MagicMock()
    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    repo_mock.get_participants.return_value = [participant]
    access = ProjectAccess(repo_mock, user_repo_mock)

    result = access.get_participants(owner, project.pid)

    assert result == [participant]
    repo_mock.get_by_id.assert_called_once_with(project.pid)
    repo_mock.get_participants.assert_called_once_with(project.pid)


def test_get_participants_by_participant():
    owner = make_user(id=1)
    participant = make_user(id=2, username="jane")
    project = make_project(owner)

    user_repo_mock = mock.MagicMock()
    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    repo_mock.is_participant.return_value = True
    repo_mock.get_participants.return_value = [participant]
    access = ProjectAccess(repo_mock, user_repo_mock, participant=True)

    result = access.get_participants(participant, project.pid)

    assert result == [participant]
    repo_mock.is_participant.assert_called_once_with(
        participant.uid, project.pid
    )


def test_get_participants_non_participant_raises():
    owner = make_user(id=1)
    outsider = make_user(id=3, username="outsider")
    project = make_project(owner)

    user_repo_mock = mock.MagicMock()
    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    repo_mock.is_participant.return_value = False
    access = ProjectAccess(repo_mock, user_repo_mock, participant=True)

    with pytest.raises(AccessError):
        access.get_participants(outsider, project.pid)


def test_get_participants_project_not_found():
    user = make_user()

    user_repo_mock = mock.MagicMock()
    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = None
    access = ProjectAccess(repo_mock, user_repo_mock)

    result = access.get_participants(user, uuid.uuid4())
    assert result is None


def test_remove_participant_by_owner():
    owner = make_user(id=1)
    participant = make_user(id=2, username="jane")
    project = make_project(owner)

    user_repo_mock = mock.MagicMock()
    user_repo_mock.get_by_username.return_value = participant
    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    repo_mock.is_participant.return_value = True
    access = ProjectAccess(repo_mock, user_repo_mock)

    access.remove_participant(owner, project.pid, participant.username)

    repo_mock.remove_participant.assert_called_once_with(
        project.pid, participant.uid
    )


def test_remove_participant_by_participant_raises_403():
    owner = make_user(id=1)
    participant = make_user(id=2, username="jane")
    project = make_project(owner)

    user_repo_mock = mock.MagicMock()
    user_repo_mock.get_by_username.return_value = participant
    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    access = ProjectAccess(repo_mock, user_repo_mock)

    with pytest.raises(AccessError):
        access.remove_participant(participant, project.pid, participant.username)


def test_remove_participant_nonexistent_project_raises():
    owner = make_user()
    user_repo_mock = mock.MagicMock()
    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = None
    access = ProjectAccess(repo_mock, user_repo_mock)

    with pytest.raises(ProjectNotFoundError):
        access.remove_participant(owner, uuid.uuid4(), "someone")


def test_remove_participant_nonexistent_user_raises():
    owner = make_user(id=1)
    project = make_project(owner)

    user_repo_mock = mock.MagicMock()
    user_repo_mock.get_by_username.return_value = None
    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    access = ProjectAccess(repo_mock, user_repo_mock)

    with pytest.raises(UserNotFoundError):
        access.remove_participant(owner, project.pid, "nonexistent")


def test_remove_participant_not_in_project_raises():
    owner = make_user(id=1)
    participant = make_user(id=2, username="jane")
    project = make_project(owner)

    user_repo_mock = mock.MagicMock()
    user_repo_mock.get_by_username.return_value = participant
    repo_mock = mock.MagicMock()
    repo_mock.get_by_id.return_value = project
    repo_mock.is_participant.return_value = False
    access = ProjectAccess(repo_mock, user_repo_mock)

    with pytest.raises(ProjectNotFoundError):
        access.remove_participant(owner, project.pid, participant.username)
