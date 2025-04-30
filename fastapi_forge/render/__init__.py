from .engines.jinja2_engine import Jinja2Engine
from .manager import RenderManager
from .registry import RendererRegistry


def create_jinja_render_manager(project_name: str) -> RenderManager:
    jinja_engine = Jinja2Engine()
    jinja_engine.add_global("project_name", project_name)
    return RenderManager(
        engine=jinja_engine,
        renderers=RendererRegistry.get_renderers(),
    )
