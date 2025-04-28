from abc import abstractmethod
from typing import Any, Protocol

from fastapi_forge.schemas import ProjectSpec


class TemplateProcessor(Protocol):
    @abstractmethod
    def process(self, spec: ProjectSpec) -> dict[str, Any]:
        raise NotImplementedError
