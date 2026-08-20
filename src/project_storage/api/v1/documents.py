import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    status,
    Response
)
from fastapi.responses import StreamingResponse

from project_storage.dependencies.authentication import get_current_user
from project_storage.dependencies.glue import FileServiceDependency
from project_storage.dependencies.project_access import (
    Action,
    require_access,
)
from project_storage.models import User
from project_storage.schemas.document import (
    CreatedDocument,
    CreatedDocumentList
)
from project_storage.exceptions.document import (
    DocumentTypeRequiredError,
    DocumentTypeNotAllowedError,
    DocumentNameRequiredError,
    DocumentSizeError,
    DocumentExistsError,
    DocumentNotFoundError,
    DocumentSaveError,
    DocumentDownloadError,
    DocumentDeleteError
)
from project_storage.error_model import ErrorModel


router = APIRouter()


@router.post(
    "",
    response_model=CreatedDocument,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {
            "model": ErrorModel,
            "description": "Document type required or not allowed"
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorModel,
            "description": "Document name required"
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorModel,
            "description": "Document already exists"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorModel,
            "description": "Failed to upload document"
        },
        status.HTTP_413_CONTENT_TOO_LARGE: {
            "model": ErrorModel,
            "description": "File size exceeds server limits"
        }
    }
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
    except DocumentTypeRequiredError:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=ErrorModel.asjson(
                project_id=project_id,
                description="Document type required"
            )
        )
    except DocumentTypeNotAllowedError as e:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=ErrorModel.asjson(
                project_id=project_id,
                document_type=e.filetype,
                description=f"Document type not allowed: {e.filetype}"
            )
        )
    except DocumentNameRequiredError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=ErrorModel.asjson(
                project_id=project_id,
                description="Document name required"
            )
        )
    except DocumentExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ErrorModel.asjson(
                project_id=project_id,
                document_name=e.filename,
                description="Document with this filename already exists"
            )
        )
    except DocumentSaveError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorModel.asjson(
                project_id=project_id,
                description="Failed to upload document"
            )
        )
    except DocumentSizeError as e:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=ErrorModel.asjson(
                project_id=project_id,
                document_id=e.filename,
                document_size=e.size,
                description="File size exceeds server limits"
            )
        )


@router.get(
    "/{document_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorModel,
            "description": "Document not found"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorModel,
            "description": "Failed to load file"
        }
    }
)
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
            detail=ErrorModel.asjson(
                project_id=project_id,
                document_id=e.file_id,
                description="Document not found"
            )
        )
    except DocumentDownloadError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorModel.asjson(
                project_id=project_id,
                document_id=document_id,
                description="Failed to load file"
            )
        )

    return StreamingResponse(
        media_type=file_meta.content_type,
        content=stream,
    )


@router.delete(
    "/{document_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorModel,
            "description": "Document not found"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorModel,
            "description": "Failed to delete file"
        }
    }
)
def remove_document(
    project_id: uuid.UUID,
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: FileServiceDependency,
    access=Depends(require_access(Action.REMOVE))
):
    try:
        service.delete(document_id, project_id)
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorModel.asjson(
                project_id=project_id,
                document_id=document_id,
                description="Document not found"
            )
        )
    except DocumentDeleteError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorModel.asjson(
                project_id=project_id,
                document_id=document_id,
                description="Failed to delete file"
            )
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
