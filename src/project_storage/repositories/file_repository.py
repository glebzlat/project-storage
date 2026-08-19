from typing import Protocol, BinaryIO


class FileRepositoryError(Exception):
    """Errors related to FileRepository"""


class FileSaveError(Exception):
    """Error saving file"""


class FileRepository(Protocol):

    def save(self, content: BinaryIO, storage_key: str) -> None:
        """Save the file contents to a persistent file storage

        Raises:
            FileSaveError: In case of any error related to file saving.
        """
