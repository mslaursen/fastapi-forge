__all__ = [
    "ArtifactBuilder",
    "AsyncIOWriter",
    "DatabaseInspector",
    "DatabaseProjectLoader",
    "FastAPIArtifactBuilder",
    "IOWriter",
    "PostgresInspector",
    "ProjectExporter",
    "ProjectLoader",
    "YamlProjectExporter",
    "YamlProjectLoader",
    "create_fastapi_artifact_builder",
    "create_postgres_project_loader",
    "create_yaml_project_exporter",
    "insert_relation_fields",
    "load_from_database",
    "load_from_yaml",
]
from pathlib import Path

from fastapi_forge.schemas import ProjectSpec

from .artifact_builder import (
    ArtifactBuilder,
    FastAPIArtifactBuilder,
    insert_relation_fields,
)
from .database import DatabaseInspector, PostgresInspector
from .exporter import ProjectExporter, YamlProjectExporter
from .io import AsyncDryRunWriter, AsyncIOWriter
from .loader import DatabaseProjectLoader, ProjectLoader, YamlProjectLoader


def load_from_yaml(path: str) -> ProjectSpec:
    return YamlProjectLoader(Path(path)).load()


def load_from_database(conn_str: str, schema: str = "public") -> ProjectSpec:
    inspector = PostgresInspector(conn_str)
    return DatabaseProjectLoader(inspector, schema).load()


def create_fastapi_artifact_builder(
    spec: ProjectSpec, dry_run: bool = False
) -> FastAPIArtifactBuilder:
    return FastAPIArtifactBuilder(
        project_spec=spec,
        io_writer=AsyncDryRunWriter() if dry_run else AsyncIOWriter(),
    )


def create_yaml_project_exporter() -> YamlProjectExporter:
    return YamlProjectExporter(
        io_writer=AsyncIOWriter(),
    )


def create_postgres_project_loader(
    conn_string: str, schema: str = "public"
) -> DatabaseProjectLoader:
    inspector = PostgresInspector(conn_string)
    return DatabaseProjectLoader(inspector, schema)
