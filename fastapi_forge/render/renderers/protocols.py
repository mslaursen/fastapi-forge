from abc import abstractmethod
from typing import Any, Protocol

from fastapi_forge.schemas import CustomEnum, Model

Renderable = Model | list[CustomEnum]


class Renderer(Protocol):
    @abstractmethod
    def render(self, data: Renderable, **kwargs: Any) -> str:
        raise NotImplementedError
