import uuid

from fastapi import status
from sqlalchemy import select

from project_storage.core.config import settings
from project_storage.database import connect
from project_storage.models import FileMeta


def test_upload_document_by_owner_returns_201(
    test_client, create_user, create_project, make_token, tmp_path
):
    owner = create_user(username="owner")
    project = create_project(owner.id)
    token = make_token(owner.username, owner.name)

    file_name = "report.pdf"
    file_content = b"%PDF-1.4 test pdf content"
    files = {"file": (file_name, file_content, "application/pdf")}

    response = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/documents",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )

    assert response.status_code == status.HTTP_201_CREATED

    stmt = select(FileMeta).where(FileMeta.filename == file_name)
    with connect() as session:
        file_meta = session.scalar(stmt)

    data = response.json()
    assert data == {
        "project_id": str(project.pid),
        "file_id": str(file_meta.fid),
        "file_name": file_name,
        "file_size": len(file_content)
    }


def test_upload_document_by_participant_returns_201(
    test_client,
    create_user,
    create_project,
    add_participant,
    make_token,
    tmp_path
):
    owner = create_user(username="owner")
    participant = create_user(username="part")
    project = create_project(owner.id)
    add_participant(project, participant)
    token = make_token(participant.username, participant.name)

    file_content = b"%PDF-1.4 participant upload"
    files = {"file": ("note.pdf", file_content, "application/pdf")}

    response = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/documents",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_upload_document_by_non_participant_returns_404(
    test_client, create_user, create_project, make_token, tmp_path
):
    owner = create_user(username="owner")
    outsider = create_user(username="outsider")
    project = create_project(owner.id)
    token = make_token(outsider.username, outsider.name)

    file_content = b"%PDF-1.4"
    files = {"file": ("x.pdf", file_content, "application/pdf")}

    response = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/documents",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_upload_document_nonexistent_project_returns_404(
    test_client, create_user, make_token, tmp_path
):
    owner = create_user(username="owner")
    token = make_token(owner.username, owner.name)

    file_content = b"%PDF-1.4"
    files = {"file": ("x.pdf", file_content, "application/pdf")}

    response = test_client.post(
        f"{settings.API_PATH}/projects/{uuid.uuid4()}/documents",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_upload_document_duplicate_filename_returns_409(
    test_client, create_user, create_project, make_token, tmp_path
):
    owner = create_user(username="owner")
    project = create_project(owner.id)
    token = make_token(owner.username, owner.name)

    file_content = b"%PDF-1.4 duplicate test"
    files = {"file": ("duplicate.pdf", file_content, "application/pdf")}

    r1 = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/documents",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert r1.status_code == status.HTTP_201_CREATED

    r2 = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/documents",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert r2.status_code == status.HTTP_409_CONFLICT
    assert r2.json() == {"detail": "Document with this filename already exists"}


def test_upload_document_unsupported_type_returns_415(
    test_client, create_user, create_project, make_token, tmp_path
):
    owner = create_user(username="owner")
    project = create_project(owner.id)
    token = make_token(owner.username, owner.name)

    file_content = b"not a pdf"
    files = {"file": ("script.exe", file_content, "application/x-msdownload")}

    response = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/documents",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )

    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    assert "File type not allowed" in response.json()["detail"]


def test_upload_document_missing_filename_returns_422(
    test_client, create_user, create_project, make_token, tmp_path
):
    owner = create_user(username="owner")
    project = create_project(owner.id)
    token = make_token(owner.username, owner.name)

    file_content = b"%PDF-1.4"
    files = {"file": ("", file_content, "application/pdf")}

    response = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/documents",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_upload_document_nonexistent_user_returns_401(
    create_user, test_client, create_project, tmp_path
):
    owner = create_user(username="useruser")
    project = create_project(owner.id)  # owner id that does not exist in token

    file_content = b"%PDF-1.4"
    files = {"file": ("x.pdf", file_content, "application/pdf")}

    response = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/documents",
        headers={"Authorization": "Bearer invalidtoken"},
        files=files,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_document_by_owner_returns_200(
    test_client, create_user, create_project, make_token, tmp_path
):
    owner = create_user(username="owner")
    project = create_project(owner.id)
    token = make_token(owner.username, owner.name)

    file_name = "report.pdf"
    file_content = b"%PDF-1.4 test pdf content"
    files = {"file": (file_name, file_content, "application/pdf")}

    upload_resp = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/documents",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert upload_resp.status_code == status.HTTP_201_CREATED
    file_id = upload_resp.json()["file_id"]

    response = test_client.get(
        f"{settings.API_PATH}/projects/{project.pid}/documents/{file_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/pdf"
    assert response.content == file_content


def test_get_document_by_participant_returns_200(
    test_client,
    create_user,
    create_project,
    add_participant,
    make_token,
    tmp_path
):
    owner = create_user(username="owner")
    participant = create_user(username="part")
    project = create_project(owner.id)
    add_participant(project, participant)
    owner_token = make_token(owner.username, owner.name)
    part_token = make_token(participant.username, participant.name)

    file_content = b"%PDF-1.4 participant download"
    files = {"file": ("note.pdf", file_content, "application/pdf")}

    upload_resp = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/documents",
        headers={"Authorization": f"Bearer {owner_token}"},
        files=files,
    )
    assert upload_resp.status_code == status.HTTP_201_CREATED
    file_id = upload_resp.json()["file_id"]

    response = test_client.get(
        f"{settings.API_PATH}/projects/{project.pid}/documents/{file_id}",
        headers={"Authorization": f"Bearer {part_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.content == file_content


def test_get_document_by_non_participant_returns_404(
    test_client, create_user, create_project, make_token, tmp_path
):
    owner = create_user(username="owner")
    outsider = create_user(username="outsider")
    project = create_project(owner.id)
    owner_token = make_token(owner.username, owner.name)
    outsider_token = make_token(outsider.username, outsider.name)

    file_content = b"%PDF-1.4"
    files = {"file": ("x.pdf", file_content, "application/pdf")}

    upload_resp = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/documents",
        headers={"Authorization": f"Bearer {owner_token}"},
        files=files,
    )
    assert upload_resp.status_code == status.HTTP_201_CREATED
    file_id = upload_resp.json()["file_id"]

    response = test_client.get(
        f"{settings.API_PATH}/projects/{project.pid}/documents/{file_id}",
        headers={"Authorization": f"Bearer {outsider_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_document_nonexistent_project_returns_404(
    test_client, create_user, make_token, tmp_path
):
    owner = create_user(username="owner")
    token = make_token(owner.username, owner.name)

    response = test_client.get(
        f"{settings.API_PATH}/projects/{uuid.uuid4()}/documents/"
        f"{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_document_nonexistent_document_returns_404(
    test_client, create_user, create_project, make_token, tmp_path
):
    owner = create_user(username="owner")
    project = create_project(owner.id)
    token = make_token(owner.username, owner.name)

    response = test_client.get(
        f"{settings.API_PATH}/projects/{project.pid}/documents/"
        f"{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_document_nonexistent_user_returns_401(
    create_user, test_client, create_project, make_token, tmp_path
):
    owner = create_user(username="owner")
    project = create_project(owner.id)
    token = make_token(owner.username, owner.name)

    file_content = b"%PDF-1.4"
    files = {"file": ("x.pdf", file_content, "application/pdf")}

    upload_resp = test_client.post(
        f"{settings.API_PATH}/projects/{project.pid}/documents",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert upload_resp.status_code == status.HTTP_201_CREATED
    file_id = upload_resp.json()["file_id"]

    response = test_client.get(
        f"{settings.API_PATH}/projects/{project.pid}/documents/{file_id}",
        headers={"Authorization": "Bearer invalidtoken"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
