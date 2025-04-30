from abc import abstractmethod
from pathlib import Path
from typing import Protocol


class IOWriter(Protocol):
    @abstractmethod
    async def write_file(self, path: Path, content: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def write_directory(self, path: Path) -> None:
        raise NotImplementedError
