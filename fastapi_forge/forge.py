import os
import shutil
import asyncio
from cookiecutter.main import cookiecutter
from fastapi_forge.dtos import ProjectSpec
from fastapi_forge.logger import logger
from fastapi_forge.project_io import ProjectBuilder


def _get_template_path() -> str:
    """Return the absolute path to the project template directory."""
    template_path = os.path.join(os.path.dirname(__file__), "template")
    if not os.path.exists(template_path):
        raise RuntimeError(f"Template directory not found: {template_path}")
    return template_path


async def _teardown_project(project_name: str) -> None:
    """Forcefully remove the project directory and all its contents."""
    project_dir = os.path.join(os.getcwd(), project_name)
    if os.path.exists(project_dir):
        await asyncio.to_thread(shutil.rmtree, project_dir)
        logger.info(f"Removed project directory: {project_dir}")


async def build_project(spec: ProjectSpec) -> None:
    """Create a new project using the provided template and specifications."""
    try:
        builder = ProjectBuilder(spec.project_name, None)
        await builder.build_artifacts(spec.models)

        template_path = _get_template_path()
        cookiecutter(
            template_path,
            output_dir=os.getcwd(),
            no_input=True,
            overwrite_if_exists=True,
            extra_context={
                **spec.model_dump(exclude={"models"}),
                "models": {
                    "models": [model.model_dump() for model in spec.models],
                },
            },
        )
        logger.info(f"Project '{spec.project_name}' created successfully.")
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        await _teardown_project(spec.project_name)
        raise
