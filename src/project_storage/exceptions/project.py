import uuid

from typing import Optional


class ProjectError(Exception):
    """Errors related to projects"""

    def __init__(
        self,
        project_name: Optional[str] = None,
        project_id: Optional[uuid.UUID] = None
    ) -> None:
        super().__init__()
        self.project_name = project_name
        self.project_id = project_id


class ProjectExistsError(ProjectError):
    """Project with the given name already exists"""


class ProjectNotFoundError(ProjectError):
    """Project not found"""
