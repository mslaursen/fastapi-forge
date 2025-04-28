__all__ = [
    "ArtifactBuilder",
    "AsyncFileWriter",
    "DatabaseInspector",
    "DatabaseProjectLoader",
    "FastAPIArtifactBuilder",
    "FileWriter",
    "PostgresInspector",
    "ProjectExporter",
    "ProjectLoader",
    "YamlProjectExporter",
    "YamlProjectLoader",
    "create_fastapi_project_builder",
    "create_postgres_project_loader",
    "create_yaml_project_exporter",
    "load_from_database",
    "load_from_yaml",
]
from pathlib import Path

from fastapi_forge.schemas import ProjectSpec

from .artifact_builder import ArtifactBuilder, FastAPIArtifactBuilder
from .database import DatabaseInspector, PostgresInspector
from .exporter import ProjectExporter, YamlProjectExporter
from .file import FileWriter
from .file.writer import AsyncFileWriter
from .loader import DatabaseProjectLoader, ProjectLoader, YamlProjectLoader


def load_from_yaml(path: str) -> ProjectSpec:
    return YamlProjectLoader(Path(path)).load()


def load_from_database(conn_str: str, schema: str = "public") -> ProjectSpec:
    inspector = PostgresInspector(conn_str)
    return DatabaseProjectLoader(inspector, schema).load()


def create_fastapi_project_builder(spec: ProjectSpec) -> FastAPIArtifactBuilder:
    return FastAPIArtifactBuilder(
        project_spec=spec,
        file_writer=AsyncFileWriter(),
    )


def create_yaml_project_exporter() -> YamlProjectExporter:
    return YamlProjectExporter(
        file_writer=AsyncFileWriter(),
    )


def create_postgres_project_loader(
    conn_string: str, schema: str = "public"
) -> DatabaseProjectLoader:
    inspector = PostgresInspector(conn_string)
    return DatabaseProjectLoader(inspector, schema)
