from typing import Any

from fastapi_forge.schemas import Model

from ..engines.base_engine import BaseTemplateEngine
from ..templates import DAO_TEMPLATE
from .base_renderer import BaseRenderer


class DAORenderer(BaseRenderer):
    def __init__(self, engine: BaseTemplateEngine):
        self.engine = engine

    def render(self, model: Model, **kwargs: Any) -> str:
        return self.engine.render(DAO_TEMPLATE, {"model": model, **kwargs})
