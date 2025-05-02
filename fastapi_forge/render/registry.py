from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from .renderers import Renderer


class RendererRegistry:
    _renderers: ClassVar[dict[str, type["Renderer"]]] = {}

    @classmethod
    def register(cls, name: str) -> Any:
        def decorator(renderer_class: type["Renderer"]) -> type["Renderer"]:
            cls._renderers[name] = renderer_class
            return renderer_class

        return decorator

    @classmethod
    def get_renderers(cls) -> dict[str, type["Renderer"]]:
        return cls._renderers.copy()
