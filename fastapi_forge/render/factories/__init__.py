from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol

from ..engines import TemplateEngine
from ..registry import RendererRegistry
from ..renderers import (
    DAORenderer,
    DTORenderer,
    EnumRenderer,
    ModelRenderer,
    RouterRenderer,
    TestDeleteRenderer,
    TestGetIdRenderer,
    TestGetRenderer,
    TestPatchRenderer,
    TestPostRenderer,
)

if TYPE_CHECKING:
    from fastapi_forge.render.renderers.protocols import Renderer


class RendererFactory(Protocol):
    @abstractmethod
    def create(self, engine: TemplateEngine) -> "Renderer":
        raise NotImplementedError


@RendererRegistry.register("model")
class ModelRendererFactory(RendererFactory):
    def create(self, engine):
        return ModelRenderer(engine)


@RendererRegistry.register("dto")
class DTORendererFactory(RendererFactory):
    def create(self, engine):
        return DTORenderer(engine)


@RendererRegistry.register("dao")
class DAORendererFactory(RendererFactory):
    def create(self, engine):
        return DAORenderer(engine)


@RendererRegistry.register("router")
class RouterRendererFactory(RendererFactory):
    def create(self, engine):
        return RouterRenderer(engine)


@RendererRegistry.register("enum")
class EnumRendererFactory(RendererFactory):
    def create(self, engine):
        return EnumRenderer(engine)


@RendererRegistry.register("test_get")
class TestGetRendererFactory(RendererFactory):
    def create(self, engine):
        return TestGetRenderer(engine)


@RendererRegistry.register("test_get_id")
class TestGetIdRendererFactory(RendererFactory):
    def create(self, engine):
        return TestGetIdRenderer(engine)


@RendererRegistry.register("test_post")
class TestPostRendererFactory(RendererFactory):
    def create(self, engine):
        return TestPostRenderer(engine)


@RendererRegistry.register("test_patch")
class TestPatchRendererFactory(RendererFactory):
    def create(self, engine):
        return TestPatchRenderer(engine)


@RendererRegistry.register("test_delete")
class TestDeleteRendererFactory(RendererFactory):
    def create(self, engine):
        return TestDeleteRenderer(engine)
