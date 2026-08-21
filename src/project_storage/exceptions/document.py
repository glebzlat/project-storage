import uuid

from typing import Optional


class DocumentError(Exception):
    """Errors related to document storage and retrieval"""


class FileMetaError(DocumentError):
    """Errors related to FileMetaRepository"""

    def __init__(
        self,
        message: str,
        filename: Optional[str] = None,
        project_id: Optional[uuid.UUID] = None,
        file_id: Optional[uuid.UUID] = None
    ) -> None:
        super().__init__(message)
        self.filename = filename
        self.project_id = project_id
        self.file_id = file_id


class FileServiceError(DocumentError):
    """Errors related to FileService"""


class DocumentTypeRequiredError(FileServiceError):
    """No content-type specified for the file"""


class DocumentTypeNotAllowedError(FileServiceError):
    """Received non-allowed content-type"""

    def __init__(self, message: str, filetype: str) -> None:
        super().__init__(message)
        self.filetype = filetype


class DocumentNameRequiredError(FileServiceError):
    """Received a file without name"""


class DocumentSizeError(FileServiceError):
    """Document size exceeds maximum limit"""

    def __init__(self, message: str, size: int) -> None:
        super().__init__(message)
        self.size = size


class DocumentExistsError(FileMetaError):
    """Document already exists on the project"""


class DocumentNotFoundError(FileMetaError):
    """Document not found"""


class DocumentSaveError(DocumentError):
    """Error saving file"""


class DocumentDownloadError(DocumentError):
    """Error downloading file"""


class DocumentDeleteError(DocumentError):
    """Error deleting file"""
