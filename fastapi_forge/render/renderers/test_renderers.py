from typing import Any

from fastapi_forge.schemas import Model

from ..engines.base_engine import BaseTemplateEngine
from ..templates import (
    TEST_DELETE_TEMPLATE,
    TEST_GET_ID_TEMPLATE,
    TEST_GET_TEMPLATE,
    TEST_PATCH_TEMPLATE,
    TEST_POST_TEMPLATE,
)
from .base_renderer import BaseRenderer


class TestPostRenderer(BaseRenderer):
    def __init__(self, engine: BaseTemplateEngine):
        self.engine = engine

    def render(self, model: Model, **kwargs: Any) -> str:
        return self.engine.render(TEST_POST_TEMPLATE, {"model": model, **kwargs})


class TestGetRenderer(BaseRenderer):
    def __init__(self, engine: BaseTemplateEngine):
        self.engine = engine

    def render(self, model: Model, **kwargs: Any) -> str:
        return self.engine.render(TEST_GET_TEMPLATE, {"model": model, **kwargs})


class TestGetIdRenderer(BaseRenderer):
    def __init__(self, engine: BaseTemplateEngine):
        self.engine = engine

    def render(self, model: Model, **kwargs: Any) -> str:
        return self.engine.render(TEST_GET_ID_TEMPLATE, {"model": model, **kwargs})


class TestPatchRenderer(BaseRenderer):
    def __init__(self, engine: BaseTemplateEngine):
        self.engine = engine

    def render(self, model: Model, **kwargs: Any) -> str:
        return self.engine.render(TEST_PATCH_TEMPLATE, {"model": model, **kwargs})


class TestDeleteRenderer(BaseRenderer):
    def __init__(self, engine: BaseTemplateEngine):
        self.engine = engine

    def render(self, model: Model, **kwargs: Any) -> str:
        return self.engine.render(TEST_DELETE_TEMPLATE, {"model": model, **kwargs})
