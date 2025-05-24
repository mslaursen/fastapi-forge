from typing import TYPE_CHECKING, Any, ClassVar

from .renderers.enums import RendererType

if TYPE_CHECKING:
    from .renderers import Renderer


class RendererRegistry:
    _renderers: ClassVar[dict[RendererType, type["Renderer"]]] = {}

    @classmethod
    def register(cls, renderer_type: RendererType) -> Any:
        def decorator(renderer_class: type["Renderer"]) -> type["Renderer"]:
            cls._renderers[renderer_type] = renderer_class
            return renderer_class

        return decorator

    @classmethod
    def get_renderers(cls) -> dict[RendererType, type["Renderer"]]:
        return cls._renderers.copy()
