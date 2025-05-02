from pathlib import PurePath

from fastapi_forge.schemas import ProjectSpec

from .protocols import ProjectValidator


class ProjectNameValidator(ProjectValidator):
    def validate(self, project_spec: ProjectSpec) -> None:
        project_name = project_spec.project_name

        if not project_name:
            msg = "Project name cannot be empty"
            raise ValueError(msg)
        if not project_name.isidentifier():
            raise ValueError(
                f"Invalid project name: {project_name}. Must be a valid identifier."
            )

        if PurePath(project_name).is_absolute():
            raise ValueError(
                f"Project name cannot be an absolute path: {project_name}."
            )

        if not project_name.isascii():
            raise ValueError(f"Project name must be ASCII: {project_name}.")
