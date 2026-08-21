from typing import BinaryIO
from io import BytesIO

from botocore.exceptions import ClientError

from project_storage.repositories.file_repository import (
    FileRepository as FileRepositoryProtocol
)
from project_storage.exceptions.document import (
    DocumentSaveError,
    DocumentDownloadError,
    DocumentDeleteError
)


class FileRepository(FileRepositoryProtocol):

    def __init__(self, s3_client) -> None:
        self._client = s3_client

    def save(self, content: BinaryIO, storage_key: str) -> None:
        try:
            self._client.upload_fileobj(
                content,
                storage_key,
            )
        except ClientError:
            raise DocumentSaveError()

    def get(self, storage_key: str) -> BinaryIO:
        stream = BytesIO()
        try:
            self._client.download_fileobj(storage_key, stream)
        except ClientError:
            raise DocumentDownloadError()
        stream.seek(0)
        return stream

    def delete(self, storage_key: str) -> None:
        try:
            self._client.delete_object(storage_key)
        except ClientError:
            raise DocumentDeleteError()
