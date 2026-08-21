import uuid

from typing import Protocol

from project_storage.models import Project


class ProjectRepository(Protocol):

    def create(self, user_id: uuid.UUID, project: Project) -> Project:
        """Create a project and make the user with the given ID its owner

        Returns:
            A new project instance from the data base.

        Raises:
            ProjectExistsError: If the project with the given name already
                exists in the list of projects for the given user.
        """

    def get_by_id(self, project_id: uuid.UUID) -> Project:
        """Get a project by id

        Returns:
            Project instance.

        Raises:
            ProjectNotFoundError: If the project with the given id does not
                exist.
        """

    def update(
        self,
        project_id: uuid.UUID,
        values: dict
    ) -> None:
        """Update a project with the values from the dictionary

        Raises:
            ProjectNotFoundError: If the project with the given id does not
                exist.
        """

    def get_all(self, user_id: uuid.UUID) -> list[Project]:
        """Get the list of projects belonging to the user

        Returns:
            The list of projects where the user with the given id is set as
                an owner.
        """

    def delete(self, project_id: uuid.UUID) -> None:
        """Delete the project

        Raises:
            ProjectNotFoundError: If the project with the given id does not
                exist.
        """
