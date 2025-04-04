import asyncio
import shutil
from pathlib import Path
from time import perf_counter

from cookiecutter.main import cookiecutter

from fastapi_forge.dtos import ProjectSpec
from fastapi_forge.logger import logger
from fastapi_forge.project_io import ProjectBuilder


def _get_template_path() -> Path:
    """Return the absolute path to the project template directory."""
    template_path = Path(__file__).parent / "template"
    if not template_path.exists():
        raise RuntimeError(f"Template directory not found: {template_path}")
    return template_path


async def _teardown_project(project_name: str) -> None:
    """Forcefully remove the project directory and all its contents."""
    project_dir = Path.cwd() / project_name
    if project_dir.exists():
        await asyncio.to_thread(shutil.rmtree, project_dir)
        logger.info(f"Removed project directory: {project_dir}")


async def build_project(spec: ProjectSpec) -> None:
    """Create a new project using the provided template and specifications."""
    try:
        start = perf_counter()
        logger.info(f"Building project '{spec.project_name}'...")

        builder = ProjectBuilder(spec)
        await builder.build_artifacts()

        template_path = str(_get_template_path())

        extra_context = {
            **spec.model_dump(exclude={"models"}),
            "models": {
                "models": [model.model_dump() for model in spec.models],
            },
        }

        if spec.use_builtin_auth:
            auth_user = spec.get_auth_model()
            if auth_user:
                extra_context["auth_model"] = auth_user.model_dump()
            else:
                logger.warning("No auth model found. Skipping authentication setup.")
                extra_context["use_builtin_auth"] = False

        cookiecutter(
            template_path,
            output_dir=str(Path.cwd()),
            no_input=True,
            overwrite_if_exists=True,
            extra_context=extra_context,
        )
        logger.info(f"Project '{spec.project_name}' created successfully.")

        end = perf_counter()
        logger.info(f"Project built in {end - start:.2f} seconds.")
    except Exception as exc:
        logger.error(f"Failed to create project: {exc}")
        await _teardown_project(spec.project_name)
        raise
