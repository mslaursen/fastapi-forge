from importlib.resources import as_file
from typing import Any
import yaml
from typing import Callable
from fastapi_forge.dtos import LoadedModel, ProjectSpec, Model
from pathlib import Path


class ProjectLoader:
    """Load project from yaml file."""

    def __init__(
        self,
        project_path: Path,
        model_generator_func: Callable[[list[dict[str, Any]]], list[Model]],
    ) -> None:
        self.project_path = project_path
        self.model_generator_func = model_generator_func

        print(f"Loading project from: {project_path}")

    def _load_project_to_dict(self) -> dict[str, Any]:
        with as_file(self.project_path) as resolved_path:
            if not resolved_path.exists():
                raise FileNotFoundError(
                    f"Project config file not found: {resolved_path}"
                )

            with open(resolved_path) as stream:
                try:
                    y = yaml.safe_load(stream)
                    return y["project"]
                except Exception as e:
                    raise e

    def load_project_spec(self) -> ProjectSpec:
        project_dict = self._load_project_to_dict()
        loaded_models = [
            LoadedModel(**model) for model in project_dict.get("models", None) or []
        ]
        models: list[Model] = self.model_generator_func(
            [m.model_dump() for m in loaded_models]
        )
        # remaining will be project config kwargs
        project_dict.pop("models")
        return ProjectSpec(
            **project_dict,
            models=models,
        )

    def load_project_dict(self) -> dict[str, Any]:
        return self._load_project_to_dict()
