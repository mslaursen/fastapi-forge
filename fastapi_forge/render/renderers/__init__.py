from typing import Any

from fastapi_forge.schemas import CustomEnum, Model

from ..engines import TemplateEngine
from ..registry import RendererRegistry
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
from .enums import RendererType
from .protocols import Renderer


@RendererRegistry.register(RendererType.MODEL)
class ModelRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            MODEL_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register(RendererType.ROUTER)
class RouterRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            ROUTERS_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register(RendererType.DAO)
class DAORenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            DAO_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register(RendererType.DTO)
class DTORenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            DTO_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register(RendererType.TEST_POST)
class TestPostRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            TEST_POST_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register(RendererType.TEST_GET)
class TestGetRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            TEST_GET_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register(RendererType.TEST_GET_ID)
class TestGetIdRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            TEST_GET_ID_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register(RendererType.TEST_PATCH)
class TestPatchRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            TEST_PATCH_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register(RendererType.TEST_DELETE)
class TestDeleteRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: Model, **kwargs: Any) -> str:
        return self.engine.render(
            TEST_DELETE_TEMPLATE,
            {"model": data, **kwargs},
        )


@RendererRegistry.register(RendererType.ENUM)
class EnumRenderer(Renderer):
    def __init__(self, engine: TemplateEngine) -> None:
        self.engine = engine

    def render(self, data: list[CustomEnum], **kwargs: Any) -> str:
        return self.engine.render(
            ENUMS_TEMPLATE,
            {"enums": data, **kwargs},
        )
