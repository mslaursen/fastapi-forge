from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from fastapi_forge.render.factories import RendererFactory


class RendererRegistry:
    _factories: ClassVar[dict[str, type["RendererFactory"]]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(factory_class: type["RendererFactory"]):
            cls._factories[name] = factory_class
            return factory_class

        return decorator

    @classmethod
    def get_factories(cls) -> dict[str, type["RendererFactory"]]:
        return cls._factories.copy()
