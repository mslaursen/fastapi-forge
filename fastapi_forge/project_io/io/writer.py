from pathlib import Path

import aiofiles

from fastapi_forge.logger import logger

from .protocols import IOWriter


class AsyncIOWriter(IOWriter):
    async def write_file(self, path: Path, content: str) -> None:
        try:
            async with aiofiles.open(path, "w") as file:
                await file.write(content)
                logger.info(f"File written successfully: {path}")
        except OSError:
            logger.error(f"Error writing file {path}")

    async def write_directory(self, path: Path) -> None:
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory created successfully: {path}")
        except OSError:
            logger.error(f"Error creating directory {path}")


class AsyncDryRunWriter(IOWriter):
    async def write_file(self, path: Path, content: str) -> None:
        logger.info(f"Dry run: {path} would be written")

    async def write_directory(self, path: Path) -> None:
        logger.info(f"Dry run: {path} directory would be created")
