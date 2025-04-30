from pathlib import Path

import yaml

from fastapi_forge.schemas import ProjectSpec

from ..io import IOWriter
from .protocols import ProjectExporter


class YamlProjectExporter(ProjectExporter):
    def __init__(self, io_writer: IOWriter):
        self.io_writer = io_writer

    async def export_project(self, project_spec: ProjectSpec) -> None:
        yaml_structure = {
            "project": project_spec.model_dump(
                round_trip=True,  # exclude computed fields
            ),
        }
        file_path = Path.cwd() / f"{project_spec.project_name}.yaml"
        await self.io_writer.write_file(
            file_path,
            yaml.dump(
                yaml_structure,
                default_flow_style=False,
                sort_keys=False,
            ),
        )
