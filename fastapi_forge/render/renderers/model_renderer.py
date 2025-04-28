from typing import Any

from fastapi_forge.schemas import Model

from ..engines.protocols import TemplateEngine
from ..templates.model import MODEL_TEMPLATE
from .protocols import Renderer


class ModelRenderer(Renderer):
    def __init__(self, engine: TemplateEngine):
        self.engine = engine

    def render(self, model: Model, **kwargs: Any) -> str:
        return self.engine.render(MODEL_TEMPLATE, {"model": model, **kwargs})
