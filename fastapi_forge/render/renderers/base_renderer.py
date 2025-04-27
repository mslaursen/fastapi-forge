from abc import ABC, abstractmethod
from typing import Any

from fastapi_forge.schemas import CustomEnum, Model

Renderable = Model | list[CustomEnum]


class BaseRenderer(ABC):
    @abstractmethod
    def render(self, data: Renderable, **kwargs: Any) -> str:
        raise NotImplementedError
