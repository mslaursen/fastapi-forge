from abc import abstractmethod
from typing import Protocol

from fastapi_forge.schemas import ProjectSpec


class ProjectExporter(Protocol):
    @abstractmethod
    async def export_project(self, project_spec: ProjectSpec) -> None:
        raise NotImplementedError
