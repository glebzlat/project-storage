from typing import Optional

from project_storage.models import User, Project


class CreateProjectUseCase:

    def __init__(self) -> None:
        pass

    def create(
        self,
        user: User,
        name: str,
        description: Optional[str]
    ) -> Project:
        ...
