from abc import abstractmethod
from pathlib import Path
from typing import Any, Protocol


class CookiecutterAdapter(Protocol):
    @abstractmethod
    def generate(
        self,
        template_path: Path,
        output_dir: Path,
        extra_context: dict[str, Any] | None = None,
    ) -> None:
        raise NotImplementedError
