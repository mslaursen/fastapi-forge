from abc import abstractmethod
from typing import Protocol


class ProjectBuilder(Protocol):
    @abstractmethod
    async def build_artifacts(self) -> None:
        raise NotImplementedError
