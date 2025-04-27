from typing import Any

from fastapi_forge.schemas import CustomEnum

from ..engines.base_engine import BaseTemplateEngine
from ..templates import ENUMS_TEMPLATE
from .base_renderer import BaseRenderer


class EnumRenderer(BaseRenderer):
    def __init__(self, engine: BaseTemplateEngine):
        self.engine = engine

    def render(self, enums: list[CustomEnum], **kwargs: Any) -> str:
        return self.engine.render(ENUMS_TEMPLATE, {"enums": enums, **kwargs})
