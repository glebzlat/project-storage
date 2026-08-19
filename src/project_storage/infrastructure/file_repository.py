from typing import BinaryIO

from botocore.exceptions import ClientError

from project_storage.repositories.file_repository import (
    FileRepository as FileRepositoryProtocol,
    FileSaveError
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
            raise FileSaveError()
