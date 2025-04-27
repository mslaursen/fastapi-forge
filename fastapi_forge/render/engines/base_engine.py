from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class BaseTemplateEngine(ABC):
    """Abstract base class for all template engines."""

    @abstractmethod
    def add_filter(self, name: str, filter_func: Callable[[Any], Any]) -> None:
        """Register a new template filter."""
        raise NotImplementedError

    @abstractmethod
    def add_global(self, name: str, value: Any) -> None:
        """Register a new global variable."""
        raise NotImplementedError

    @abstractmethod
    def render(self, template: str, context: dict[str, Any]) -> str:
        """Render template with given context."""
        raise NotImplementedError
