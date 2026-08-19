import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    UploadFile,
    status,
)

from project_storage.dependencies.authentication import get_current_user
from project_storage.dependencies.glue import FileServiceDependency
from project_storage.dependencies.project_access import (
    Action,
    require_access,
)
from project_storage.models import User
from project_storage.repositories.file_meta_repository import (
    DocumentExistsError,
)
from project_storage.repositories.file_repository import FileSaveError
from project_storage.services.file_service import (
    FileTypeRequiredError,
    FileTypeNotAllowedError,
    FileNameRequiredError
)


router = APIRouter()


@router.post("")
def upload_document(
    project_id: uuid.UUID,
    file: UploadFile,
    current_user: Annotated[User, Depends(get_current_user)],
    service: FileServiceDependency,
    access=Depends(require_access(Action.UPLOAD))
):
    try:
        service.save(
            content=file.file,
            filename=file.filename,
            filetype=file.content_type,
            project_id=project_id,
            user_id=current_user.uid,
        )
        return Response(status_code=status.HTTP_201_CREATED)
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
