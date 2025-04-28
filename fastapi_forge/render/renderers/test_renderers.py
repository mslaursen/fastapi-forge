from typing import Any

from fastapi_forge.schemas import Model

from ..engines.protocols import TemplateEngine
from ..templates import (
    TEST_DELETE_TEMPLATE,
    TEST_GET_ID_TEMPLATE,
    TEST_GET_TEMPLATE,
    TEST_PATCH_TEMPLATE,
    TEST_POST_TEMPLATE,
)
from .protocols import Renderer


class TestPostRenderer(Renderer):
    def __init__(self, engine: TemplateEngine):
        self.engine = engine

    def render(self, model: Model, **kwargs: Any) -> str:
        return self.engine.render(TEST_POST_TEMPLATE, {"model": model, **kwargs})


class TestGetRenderer(Renderer):
    def __init__(self, engine: TemplateEngine):
        self.engine = engine

    def render(self, model: Model, **kwargs: Any) -> str:
        return self.engine.render(TEST_GET_TEMPLATE, {"model": model, **kwargs})


class TestGetIdRenderer(Renderer):
    def __init__(self, engine: TemplateEngine):
        self.engine = engine

    def render(self, model: Model, **kwargs: Any) -> str:
        return self.engine.render(TEST_GET_ID_TEMPLATE, {"model": model, **kwargs})


class TestPatchRenderer(Renderer):
    def __init__(self, engine: TemplateEngine):
        self.engine = engine

    def render(self, model: Model, **kwargs: Any) -> str:
        return self.engine.render(TEST_PATCH_TEMPLATE, {"model": model, **kwargs})


class TestDeleteRenderer(Renderer):
    def __init__(self, engine: TemplateEngine):
        self.engine = engine

    def render(self, model: Model, **kwargs: Any) -> str:
        return self.engine.render(TEST_DELETE_TEMPLATE, {"model": model, **kwargs})
