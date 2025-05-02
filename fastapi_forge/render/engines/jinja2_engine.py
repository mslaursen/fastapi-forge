# render/engines/jinja2_engine.py
from collections.abc import Callable
from typing import Any

from jinja2 import Environment

from ..filters import JinjaFilters
from .protocols import TemplateEngine


class Jinja2Engine(TemplateEngine):
    def __init__(self) -> None:
        self.env = Environment()
        self._register_core_filters()

    def _register_core_filters(self) -> None:
        """Register all built-in filters"""
        self.add_filter(
            "generate_field",
            JinjaFilters.generate_field,
        )
        self.add_filter(
            "generate_relationship",
            JinjaFilters.generate_relationship,
        )

    def add_filter(self, name: str, filter_func: Callable[[Any], Any]) -> None:
        self.env.filters[name] = filter_func

    def add_global(self, name: str, value: Any) -> None:
        self.env.globals[name] = value

    def render(self, template: str, context: dict[str, Any]) -> str:
        return self.env.from_string(template).render(**context)
