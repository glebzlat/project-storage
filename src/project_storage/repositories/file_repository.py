from typing import Protocol, BinaryIO


class FileRepositoryError(Exception):
    """Errors related to FileRepository"""


class FileSaveError(FileRepositoryError):
    """Error saving file"""


class FileDownloadError(FileRepositoryError):
    """Error downloading file"""


class FileRepository(Protocol):

    def save(self, content: BinaryIO, storage_key: str) -> None:
        """Save the file contents to a persistent file storage

        Raises:
            FileSaveError: In case of any error related to file saving.
        """

    def get(self, storage_key: str) -> BinaryIO:
        """Get the file from a persistent file storage

        Raises:
            FileDownloadError: In case of download error.
        """
