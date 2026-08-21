from typing import Protocol, BinaryIO


class FileRepository(Protocol):

    def save(self, content: BinaryIO, storage_key: str) -> None:
        """Save the file contents to a persistent file storage

        Raises:
            DocumentSaveError: In case of any error related to file saving.
        """

    def get(self, storage_key: str) -> BinaryIO:
        """Get the file from a persistent file storage

        Raises:
            DocumentDownloadError: In case of download error.
        """

    def delete(self, storage_key: str) -> None:
        """Delete the file

        Raises:
            DocumentDeletionError: In case of deletion error.
        """
