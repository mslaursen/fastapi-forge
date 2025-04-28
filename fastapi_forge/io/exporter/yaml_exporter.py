from pathlib import Path

import yaml

from fastapi_forge.schemas import ProjectSpec

from ..file import FileWriter
from .protocols import ProjectExporter


class YamlProjectExporter(ProjectExporter):
    def __init__(self, file_writer: FileWriter):
        self.file_writer = file_writer

    async def export_project(self, project_spec: ProjectSpec) -> None:
        yaml_structure = {
            "project": project_spec.model_dump(
                round_trip=True,  # exclude computed fields
            ),
        }
        file_path = Path.cwd() / f"{project_spec.project_name}.yaml"
        await self.file_writer.write(
            file_path,
            yaml.dump(
                yaml_structure,
                default_flow_style=False,
                sort_keys=False,
            ),
        )
