import uuid

from typing import Protocol, Optional

from project_storage.models import FileMeta


class FileMetaError(Exception):
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


class DocumentExistsError(FileMetaError):
    """File with the given filename already exists"""


class DocumentNotFoundError(FileMetaError):
    """File not found"""


class FileMetaRepository(Protocol):

    def save(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        file_meta: FileMeta
    ) -> FileMeta:
        """Save file meta-info to the database

        Returns:
            FileMeta instance loaded from the database.

        Raises:
            FileExistsError: If file with the given filename already exists
                on the project.
        """

    def get_by_filename(
        self,
        project_id: uuid.UUID,
        filename: str
    ) -> FileMeta:
        """Retrieve file meta-info by filename

        Returns:
            FileMeta instance loaded from the database.

        Raises:
            FileNotFoundError: If no file with the given filename found on
                the project.
        """

    def get_by_id(self, file_id: uuid.UUID) -> FileMeta:
        """Retrieve file meta-info by file_id

        Returns:
            FileMeta instance loaded from the database.

        Raises:
            FileNotFoundError: If no file with the given id found.
        """
