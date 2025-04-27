from typing import Any

from fastapi_forge.schemas import Model

from ..engines.base_engine import BaseTemplateEngine
from ..renderers.base_renderer import BaseRenderer
from ..templates.model import MODEL_TEMPLATE


class ModelRenderer(BaseRenderer):
    def __init__(self, engine: BaseTemplateEngine):
        self.engine = engine

    def render(self, model: Model, **kwargs: Any) -> str:
        return self.engine.render(MODEL_TEMPLATE, {"model": model, **kwargs})
