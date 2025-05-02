from abc import abstractmethod
from typing import Any, Protocol

from fastapi_forge.render.engines.protocols import TemplateEngine
from fastapi_forge.schemas import CustomEnum, Model

Renderable = Model | list[CustomEnum]


class Renderer(Protocol):
    engine: TemplateEngine

    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    @abstractmethod
    def render(self, data: Renderable, **kwargs: Any) -> str:
        """Render the given data using the template engine."""
        raise NotImplementedError
