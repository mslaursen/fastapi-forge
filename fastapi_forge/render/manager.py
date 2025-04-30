from .engines import TemplateEngine
from .renderers import Renderer


class RenderManager:
    def __init__(
        self,
        engine: TemplateEngine,
        renderers: dict[str, type[Renderer]],
    ):
        self.engine = engine
        self.renderers = renderers
        self._renderers: dict[str, Renderer] = {}

    def get_renderer(self, renderer_type: str) -> Renderer:
        """Get a renderer instance for the specified type."""
        if renderer_type not in self.renderers:
            raise ValueError(
                f"No renderer registered for renderer type: {renderer_type}"
            )

        if renderer_type not in self._renderers:
            renderer_class = self.renderers[renderer_type]
            renderer_instance = renderer_class(self.engine)
            self._renderers[renderer_type] = renderer_instance

        return self._renderers[renderer_type]
