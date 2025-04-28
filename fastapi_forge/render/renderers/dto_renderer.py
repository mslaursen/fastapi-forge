from typing import Any

from fastapi_forge.schemas import Model

from ..engines.protocols import TemplateEngine
from ..templates import DTO_TEMPLATE
from .protocols import Renderer


class DTORenderer(Renderer):
    def __init__(self, engine: TemplateEngine):
        self.engine = engine

    def render(self, model: Model, **kwargs: Any) -> str:
        return self.engine.render(DTO_TEMPLATE, {"model": model, **kwargs})
