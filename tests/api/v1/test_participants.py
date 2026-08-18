import uuid

from fastapi import status

from project_storage.core.config import settings


def test_add_participant_by_owner_returns_204(
    test_client, create_user, create_project, make_token
):
    owner = create_user(username="owner_add_1")
    participant = create_user(username="part_add_1")
    project = create_project(owner.id)
    token = make_token(owner.username, owner.name)

    response = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/participants",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": participant.username}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_add_participant_by_non_owner_returns_403(
    test_client, create_user, create_project, add_participant, make_token
):
    owner = create_user(username="owner_add_2")
    other = create_user(username="other_add_2")
    participant = create_user(username="part_add_2")
    project = create_project(owner.id)
    add_participant(project, participant)
    token = make_token(participant.username, participant.name)

    response = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/participants",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": other.username}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_add_participant_nonexistent_project_returns_404(
    test_client, create_user, make_token
):
    owner = create_user(username="owner_add_3")
    token = make_token(owner.username, owner.name)

    response = test_client.post(
        f"{settings.API_PATH}/projects/{uuid.uuid4()}/participants",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "someone"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_participant_nonexistent_user_returns_404(
    test_client, create_user, create_project, make_token
):
    owner = create_user(username="owner_add_4")
    project = create_project(owner.id)
    token = make_token(owner.username, owner.name)

    response = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/participants",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "nonexistent_user_xyz"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_participant_duplicate_returns_409(
    test_client, create_user, create_project, make_token
):
    owner = create_user(username="owner_add_5")
    participant = create_user(username="part_add_5")
    project = create_project(owner.id)
    token = make_token(owner.username, owner.name)

    r1 = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/participants",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": participant.username}
    )
    assert r1.status_code == status.HTTP_204_NO_CONTENT

    r2 = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/participants",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": participant.username}
    )
    assert r2.status_code == status.HTTP_409_CONFLICT


def test_get_participants_by_owner(
    test_client, create_user, create_project, make_token
):
    owner = create_user(username="owner_get_1")
    p1 = create_user(username="part_get_1")
    p2 = create_user(username="part_get_2")
    project = create_project(owner.id)
    token = make_token(owner.username, owner.name)

    test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/participants",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": p1.username}
    )
    test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/participants",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": p2.username}
    )

    response = test_client.get(
        f"{settings.API_PATH}/projects/{project.pid}/participants",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["n"] == 2
    usernames = [p["username"] for p in data["participants"]]
    assert p1.username in usernames
    assert p2.username in usernames


def test_get_participants_by_participant(
    test_client, create_user, create_project, make_token
):
    owner = create_user(username="owner_get_2")
    participant = create_user(username="part_get_3")
    project = create_project(owner.id)
    owner_token = make_token(owner.username, owner.name)
    part_token = make_token(participant.username, participant.name)

    test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/participants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"username": participant.username}
    )

    response = test_client.get(
        f"{settings.API_PATH}/projects/{project.pid}/participants",
        headers={"Authorization": f"Bearer {part_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["n"] == 1


def test_get_participants_non_participant_returns_404(
    test_client, create_user, create_project, make_token
):
    owner = create_user(username="owner_get_3")
    outsider = create_user(username="outsider_get")
    project = create_project(owner.id)
    outsider_token = make_token(outsider.username, outsider.name)

    response = test_client.get(
        f"{settings.API_PATH}/projects/{project.pid}/participants",
        headers={"Authorization": f"Bearer {outsider_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_participants_nonexistent_project_returns_404(
    test_client, create_user, make_token
):
    owner = create_user(username="owner_get_4")
    token = make_token(owner.username, owner.name)

    response = test_client.get(
        f"{settings.API_PATH}/projects/{uuid.uuid4()}/participants",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_participant_by_owner(
    test_client, create_user, create_project, make_token
):
    owner = create_user(username="owner_rem_1")
    participant = create_user(username="part_rem_1")
    project = create_project(owner.id)
    token = make_token(owner.username, owner.name)

    test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/participants",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": participant.username}
    )

    response = test_client.delete(
        f"{settings.API_PATH}/projects/{project.pid}/"
        f"participants/{participant.username}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_remove_participant_by_participant_returns_403(
    test_client, create_user, create_project, make_token
):
    owner = create_user(username="owner_rem_2")
    participant = create_user(username="part_rem_2")
    project = create_project(owner.id)
    owner_token = make_token(owner.username, owner.name)
    part_token = make_token(participant.username, participant.name)

    test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/participants",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"username": participant.username}
    )

    response = test_client.delete(
        f"{settings.API_PATH}/projects/{project.pid}"
        f"/participants/{participant.username}",
        headers={"Authorization": f"Bearer {part_token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_remove_participant_nonexistent_project_returns_404(
    test_client, create_user, make_token
):
    owner = create_user(username="owner_rem_3")
    token = make_token(owner.username, owner.name)

    response = test_client.delete(
        f"{settings.API_PATH}/projects/{uuid.uuid4()}/participants/someuser",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_non_participant_returns_404(
    test_client, create_user, create_project, make_token
):
    owner = create_user(username="owner_rem_4")
    non_participant = create_user(username="not_a_part")
    project = create_project(owner.id)
    token = make_token(owner.username, owner.name)

    response = test_client.delete(
        f"{settings.API_PATH}/projects/{project.pid}"
        f"/participants/{non_participant.username}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_participant_nonexistent_user_returns_404(
    test_client, create_user, create_project, make_token
):
    owner = create_user(username="owner_rem_5")
    project = create_project(owner.id)
    token = make_token(owner.username, owner.name)

    response = test_client.delete(
        f"{settings.API_PATH}/projects/{project.pid}"
        f"/participants/nonexistent_xyz",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
