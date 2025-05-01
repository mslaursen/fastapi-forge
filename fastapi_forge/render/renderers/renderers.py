from typing import Any

from fastapi_forge.render.engines.protocols import TemplateEngine
from fastapi_forge.render.registry import RendererRegistry
from fastapi_forge.schemas import CustomEnum, Model

from ..templates import (
    DAO_TEMPLATE,
    DTO_TEMPLATE,
    ENUMS_TEMPLATE,
    MODEL_TEMPLATE,
    ROUTERS_TEMPLATE,
    TEST_DELETE_TEMPLATE,
    TEST_GET_ID_TEMPLATE,
    TEST_GET_TEMPLATE,
    TEST_PATCH_TEMPLATE,
    TEST_POST_TEMPLATE,
)
from .protocols import Renderer


@RendererRegistry.register("model")
class ModelRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            MODEL_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register("router")
class RouterRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            ROUTERS_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register("dao")
class DAORenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            DAO_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register("dto")
class DTORenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            DTO_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register("test_post")
class TestPostRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            TEST_POST_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register("test_get")
class TestGetRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            TEST_GET_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register("test_get_id")
class TestGetIdRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            TEST_GET_ID_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register("test_patch")
class TestPatchRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            TEST_PATCH_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register("test_delete")
class TestDeleteRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            TEST_DELETE_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register("enum")
class EnumRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: list[CustomEnum], **kwargs: Any) -> str:
        return self.engine.render(
            ENUMS_TEMPLATE,
            {"enums": data, **kwargs},
        )
