from typing import Protocol, Any


class UseCase(Protocol):

    def execute(self, request: Any) -> Any:
        ...
