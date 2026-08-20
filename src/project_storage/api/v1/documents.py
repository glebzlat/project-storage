import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse

from project_storage.dependencies.authentication import get_current_user
from project_storage.dependencies.glue import FileServiceDependency
from project_storage.dependencies.project_access import (
    Action,
    require_access,
)
from project_storage.models import User
from project_storage.repositories.file_meta_repository import (
    DocumentExistsError,
    DocumentNotFoundError
)
from project_storage.repositories.file_repository import (
    FileSaveError,
    FileDownloadError
)
from project_storage.services.file_service import (
    FileTypeRequiredError,
    FileTypeNotAllowedError,
    FileNameRequiredError,
    FileSizeError
)
from project_storage.schemas.document import (
    CreatedDocument,
    CreatedDocumentList
)


router = APIRouter()


@router.post(
    "",
    response_model=CreatedDocument,
    status_code=status.HTTP_201_CREATED
)
def upload_document(
    project_id: uuid.UUID,
    file: UploadFile,
    current_user: Annotated[User, Depends(get_current_user)],
    service: FileServiceDependency,
    access=Depends(require_access(Action.UPLOAD))
):
    try:
        file_meta = service.save(
            content=file.file,
            filename=file.filename,
            filetype=file.content_type,
            project_id=project_id,
            user_id=current_user.uid,
        )
        response = CreatedDocument(
            project_id=project_id,
            file_id=file_meta.fid,
            file_name=file_meta.filename,
            file_size=file_meta.size
        )
        return response
    except FileTypeRequiredError:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File type required"
        )
    except FileTypeNotAllowedError as e:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type not allowed: {e.filetype}"
        )
    except FileNameRequiredError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="File name required"
        )
    except DocumentExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document with this filename already exists"
        )
    except FileSaveError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


@router.get("/{document_id}")
def get_document(
    project_id: uuid.UUID,
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: FileServiceDependency,
    access=Depends(require_access(Action.READ))
):
    try:
        file_meta, stream = service.get(document_id, project_id)
    except DocumentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {e.file_id} not found"
        )
    except FileDownloadError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load file"
        )
    except FileSizeError as e:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File size exceeds server limits: {e.size}"
        )

    return StreamingResponse(
        media_type=file_meta.content_type,
        content=stream,
    )


@router.get("")
def list_documents(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: FileServiceDependency,
    access=Depends(require_access(Action.READ))
):
    file_metas = service.list(project_id)
    response = CreatedDocumentList(n=len(file_metas), documents=[])
    for meta in file_metas:
        doc = CreatedDocument(
            project_id=project_id,
            file_id=meta.fid,
            file_name=meta.filename,
            file_size=meta.size
        )
        response.documents.append(doc)
    return response
