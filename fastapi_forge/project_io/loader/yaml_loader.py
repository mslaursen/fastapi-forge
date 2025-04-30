from pathlib import Path
from typing import Any

import yaml

from fastapi_forge.schemas import ProjectSpec

from .protocols import ProjectLoader


class YamlProjectLoader(ProjectLoader):
    def __init__(self, project_path: Path):
        self.project_path = project_path

    def _load_project_to_dict(self) -> dict[str, Any]:
        if not self.project_path.exists():
            raise FileNotFoundError(
                f"Project config file not found: {self.project_path}"
            )

        with self.project_path.open() as stream:
            return yaml.safe_load(stream)["project"]

    def load(self) -> ProjectSpec:
        return ProjectSpec(**self._load_project_to_dict())
