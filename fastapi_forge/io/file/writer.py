from pathlib import Path

import aiofiles

from fastapi_forge.logger import logger

from .protocols import FileWriter


class AsyncFileWriter(FileWriter):
    async def write(self, path: Path, content: str) -> None:
        try:
            async with aiofiles.open(path, "w") as file:
                await file.write(content)
                logger.info(f"File written successfully: {path}")
        except OSError:
            logger.error(f"Error writing file {path}")
