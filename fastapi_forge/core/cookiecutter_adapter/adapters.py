from pathlib import Path
from typing import Any

from cookiecutter.main import cookiecutter

from fastapi_forge.logger import logger

from .protocols import CookiecutterAdapter


class OverwriteCookiecutterAdapter(CookiecutterAdapter):
    def generate(
        self,
        template_path: Path,
        output_dir: Path,
        extra_context: dict[str, Any] | None = None,
    ) -> None:
        cookiecutter(
            template=str(template_path),
            output_dir=str(output_dir),
            no_input=True,
            overwrite_if_exists=True,
            extra_context=extra_context,
        )


class DryRunCookiecutterAdapter(CookiecutterAdapter):
    def generate(
        self,
        template_path: Path,
        output_dir: Path,
        extra_context: dict[str, Any] | None = None,
    ) -> None:
        logger.info(f"Dry run mode kwargs: {template_path=}, {output_dir=}")
