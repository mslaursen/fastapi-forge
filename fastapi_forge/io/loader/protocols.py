from abc import abstractmethod
from typing import Protocol

from fastapi_forge.schemas import ProjectSpec


class ProjectLoader(Protocol):
    @abstractmethod
    def load(self) -> ProjectSpec:
        raise NotImplementedError
