import uuid

from typing import Protocol

from project_storage.models import FileMeta


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
            DocumentExistsError: If file with the given filename already exists
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
            DocumentNotFoundError: If no file with the given filename found on
                the project.
        """

    def get_by_id(self, file_id: uuid.UUID) -> FileMeta:
        """Retrieve file meta-info by file_id

        Returns:
            FileMeta instance loaded from the database.

        Raises:
            DocumentNotFoundError: If no file with the given id found.
        """

    def get(self, file_id: uuid.UUID, project_id: uuid.UUID) -> FileMeta:
        """Retrieve metadata of the file in relation to the project

        Returns:
            FileMeta instance loaded from the database.

        Raises:
            DocumentNotFoundError: If no file with the given id found on the
                project.
        """

    def delete(self, file_meta: FileMeta) -> None:
        """Delete file metadata"""

    def list(self, project_id: uuid.UUID) -> list[FileMeta]:
        """Return a list of file metadata belonging to a project

        Returns:
            List of FileMeta instances.
        """
