from typing import Any
from .registry import RendererRegistry
from .manager import RenderManager
from .engines.jinja2_engine import Jinja2Engine


def create_jinja_render_manager(project_name: str) -> RenderManager:
    jinja_engine = Jinja2Engine()
    jinja_engine.add_global("project_name", project_name)
    return RenderManager(
        engine=jinja_engine,
        factories=RendererRegistry.get_factories(),
    )
