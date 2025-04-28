from abc import abstractmethod
from pathlib import Path
from typing import Protocol


class FileWriter(Protocol):
    @abstractmethod
    async def write(self, path: Path, content: str) -> None:
        raise NotImplementedError
