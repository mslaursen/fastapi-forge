from abc import abstractmethod
from typing import Protocol

from fastapi_forge.schemas import ProjectSpec


class ProjectValidator(Protocol):
    @abstractmethod
    def validate(self, project_spec: ProjectSpec) -> None:
        raise NotImplementedError
