from abc import abstractmethod
from typing import Protocol


class ArtifactBuilder(Protocol):
    @abstractmethod
    async def build_artifacts(self) -> None:
        raise NotImplementedError
