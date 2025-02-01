import os
from cookiecutter.main import cookiecutter
from .dtos import ProjectSpec
from .utils import build_project_artifacts


def _get_template_path() -> str:
    """Returns the absolute path to the project template directory."""
    return os.path.join(os.path.dirname(__file__), "template")


def _validate_template_path(path: str) -> None:
    """Validates the existence of the template directory."""
    if not os.path.exists(path):
        raise RuntimeError(f"Template directory not found: {path}")


def forge_project(spec: ProjectSpec) -> None:
    """Creates a new project using the provided template."""

    template_path = _get_template_path()
    _validate_template_path(template_path)

    build_project_artifacts(spec.project_name, spec.models)

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
