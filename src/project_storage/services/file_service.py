import uuid
import logging

from typing import BinaryIO, Optional

from project_storage.models import FileMeta
from project_storage.repositories.file_meta_repository import (
    FileMetaRepository
)
from project_storage.repositories.file_repository import FileRepository
from project_storage.core.config import settings
from project_storage.exceptions.document import (
    DocumentExistsError,
    DocumentNotFoundError,
    DocumentNameRequiredError,
    DocumentSizeError,
    DocumentTypeNotAllowedError,
    DocumentTypeRequiredError
)


_logger = logging.getLogger("file_service")


ALLOWED_FILE_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]


class FileService:

    def __init__(
        self,
        file_repository: FileRepository,
        file_meta_repository: FileMetaRepository
    ) -> None:
        self._file_repository = file_repository
        self._file_meta_repository = file_meta_repository

    def save(
        self,
        content: BinaryIO,
        filename: Optional[str],
        filetype: Optional[str],
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> FileMeta:
        _logger.debug(
            "Saving file: filename=%s filetype=%s project_id=%s user_id=%s",
            filename, filetype, project_id, user_id
        )

        if filetype is None:
            raise DocumentTypeRequiredError("No filetype received")
        if filetype not in ALLOWED_FILE_TYPES:
            raise DocumentTypeNotAllowedError("Filetype not allowed", filetype)
        if filename is None:
            raise DocumentNameRequiredError("No filename received")

        max_file_size = settings.UPLOAD_FILE_MAX_SIZE_B
        file_size = self._get_file_size(content)
        if file_size > max_file_size:
            raise DocumentSizeError(
                "filesize exceeds maximum limit",
                size=file_size
            )

        _logger.debug("Saving file: size=%s", file_size)

        file_meta = FileMeta(
            filename=filename,
            content_type=filetype,
            size=file_size,
            storage_key=uuid.uuid4()
        )

        try:
            self._file_meta_repository.get_by_filename(project_id, filename)
        except DocumentNotFoundError:
            pass
        else:
            raise DocumentExistsError(
                "file already exists",
                project_id=project_id,
                filename=filename,
                file_id=None,
            )

        self._file_repository.save(content, str(file_meta.storage_key))
        return self._file_meta_repository.save(project_id, user_id, file_meta)

    def get_meta_by_filename(
        self,
        project_id: uuid.UUID,
        filename: str
    ) -> FileMeta:
        return self._file_meta_repository.get_by_filename(project_id, filename)

    def get_meta_by_id(self, file_id: uuid.UUID) -> FileMeta:
        return self._file_meta_repository.get_by_id(file_id)

    def get(
        self,
        file_id: uuid.UUID,
        project_id: uuid.UUID
    ) -> tuple[FileMeta, BinaryIO]:
        file_meta = self._file_meta_repository.get(file_id, project_id)
        stream = self._file_repository.get(str(file_meta.storage_key))
        return (file_meta, stream)

    def delete(self, file_id: uuid.UUID, project_id: uuid.UUID) -> None:
        file_meta = self._file_meta_repository.get(file_id, project_id)
        self._file_repository.delete(str(file_meta.storage_key))
        self._file_meta_repository.delete(file_meta)

    def list(self, project_id: uuid.UUID) -> list[FileMeta]:
        return self._file_meta_repository.list(project_id)

    def delete_resources(self, project_id: uuid.UUID) -> None:
        file_metas = self.list(project_id)
        for meta in file_metas:
            self._file_repository.delete(str(meta.storage_key))

    def _get_file_size(self, stream: BinaryIO) -> int:
        chunk_size = settings.UPLOAD_FILE_CHUNK_SIZE_B
        total_size = 0
        while chunk := stream.read(chunk_size):
            total_size += len(chunk)
        stream.seek(0)
        return total_size
