from .engines import BaseTemplateEngine
from .factories import RendererFactory
from .renderers.base_renderer import BaseRenderer


class RenderManager:
    def __init__(
        self,
        engine: BaseTemplateEngine,
        factories: dict[str, type[RendererFactory]],
    ):
        self.engine = engine
        self.factories = factories
        self._renderers: dict[str, BaseRenderer] = {}

    def get_renderer(self, renderer_type: str) -> BaseRenderer:
        """Get a renderer instance for the specified type."""
        if renderer_type not in self.factories:
            raise ValueError(
                f"No factory registered for renderer type: {renderer_type}"
            )

        if renderer_type not in self._renderers:
            factory_class = self.factories[renderer_type]
            factory_instance = factory_class()
            self._renderers[renderer_type] = factory_instance.create(
                self.engine,
            )

        return self._renderers[renderer_type]
