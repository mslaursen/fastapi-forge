from abc import abstractmethod
from collections.abc import Callable
from typing import Any, Protocol


class TemplateEngine(Protocol):
    @abstractmethod
    def add_filter(self, name: str, filter_func: Callable[[Any], Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_global(self, name: str, value: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def render(self, template: str, context: dict[str, Any]) -> str:
        raise NotImplementedError
