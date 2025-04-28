from typing import Any

from fastapi_forge.schemas import CustomEnum

from ..engines.protocols import TemplateEngine
from ..templates import ENUMS_TEMPLATE
from .protocols import Renderer


class EnumRenderer(Renderer):
    def __init__(self, engine: TemplateEngine):
        self.engine = engine

    def render(self, enums: list[CustomEnum], **kwargs: Any) -> str:
        return self.engine.render(ENUMS_TEMPLATE, {"enums": enums, **kwargs})
