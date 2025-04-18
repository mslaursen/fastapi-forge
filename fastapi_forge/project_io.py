import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import aiofiles
import click
import psycopg2
import yaml

from fastapi_forge.dtos import (
    Model,
    ModelField,
    ModelFieldMetadata,
    ModelRelationship,
    ProjectSpec,
)
from fastapi_forge.enums import FieldDataTypeEnum, HTTPMethodEnum
from fastapi_forge.jinja import (
    render_custom_enums_to_enums,
    render_model_to_dao,
    render_model_to_delete_test,
    render_model_to_dto,
    render_model_to_get_id_test,
    render_model_to_get_test,
    render_model_to_model,
    render_model_to_patch_test,
    render_model_to_post_test,
    render_model_to_routers,
)
from fastapi_forge.logger import logger
from fastapi_forge.string_utils import camel_to_snake


def _inspect_postgres_schema(
    connection_string: str, schema: str = "public"
) -> dict[str, Any]:
    logger.info(f"Querying database schema from: {connection_string}")
    try:
        parsed = urlparse(connection_string)
        if parsed.scheme != "postgresql":
            msg = "Connection string must start with 'postgresql://'"
            raise ValueError(msg)

        db_name = parsed.path[1:]
        if not db_name:
            msg = "Database name not found in connection string"
            raise ValueError(msg)

        conn = psycopg2.connect(connection_string)
        cur = conn.cursor()

        query = """
        WITH foreign_keys AS (
            SELECT
                tc.table_schema,
                tc.table_name,
                kcu.column_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM
                information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
        ),
        primary_keys AS (
            SELECT
                tc.table_schema,
                tc.table_name,
                kcu.column_name,
                TRUE AS is_primary_key
            FROM
                information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
            WHERE
                tc.constraint_type = 'PRIMARY KEY'
        ),
        unique_constraints AS (
            SELECT
                tc.table_schema,
                tc.table_name,
                kcu.column_name,
                TRUE AS is_unique
            FROM
                information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
            WHERE
                tc.constraint_type = 'UNIQUE'
        ),
        indexes AS (
            SELECT
                n.nspname AS table_schema,
                t.relname AS table_name,
                a.attname AS column_name,
                TRUE AS is_indexed
            FROM
                pg_class t,
                pg_class i,
                pg_index ix,
                pg_attribute a,
                pg_namespace n
            WHERE
                t.oid = ix.indrelid
                AND i.oid = ix.indexrelid
                AND a.attrelid = t.oid
                AND a.attnum = ANY(ix.indkey)
                AND t.relnamespace = n.oid
                AND n.nspname = %s
        ),
        column_defaults AS (
            SELECT
                table_schema,
                table_name,
                column_name,
                column_default
            FROM
                information_schema.columns
            WHERE
                table_schema = %s
                AND column_default IS NOT NULL
        )
        SELECT
            t.table_schema,
            t.table_name,
            json_agg(
                json_build_object(
                    'name', c.column_name,
                    'type', c.data_type,
                    'nullable', c.is_nullable = 'YES',
                    'primary_key', COALESCE(pk.is_primary_key, FALSE),
                    'unique', COALESCE(uc.is_unique, FALSE),
                    'index', COALESCE(idx.is_indexed, FALSE),
                    'default', cd.column_default,
                    'foreign_key',
                    CASE WHEN fk.foreign_table_name IS NOT NULL THEN
                        json_build_object(
                            'field_name', c.column_name,
                            'target_model', fk.foreign_table_name
                        )
                    ELSE NULL END
                )
                ORDER BY c.ordinal_position
            ) AS columns
        FROM
            information_schema.tables t
            JOIN information_schema.columns c
                ON t.table_schema = c.table_schema
                AND t.table_name = c.table_name
            LEFT JOIN foreign_keys fk
                ON t.table_schema = fk.table_schema
                AND t.table_name = fk.table_name
                AND c.column_name = fk.column_name
            LEFT JOIN primary_keys pk
                ON t.table_schema = pk.table_schema
                AND t.table_name = pk.table_name
                AND c.column_name = pk.column_name
            LEFT JOIN unique_constraints uc
                ON t.table_schema = uc.table_schema
                AND t.table_name = uc.table_name
                AND c.column_name = uc.column_name
            LEFT JOIN indexes idx
                ON t.table_schema = idx.table_schema
                AND t.table_name = idx.table_name
                AND c.column_name = idx.column_name
            LEFT JOIN column_defaults cd
                ON t.table_schema = cd.table_schema
                AND t.table_name = cd.table_name
                AND c.column_name = cd.column_name
        WHERE
            t.table_schema = %s
            AND t.table_type = 'BASE TABLE'
        GROUP BY
            t.table_schema, t.table_name
        ORDER BY
            t.table_schema, t.table_name;
        """

        cur.execute(query, (schema, schema, schema))
        tables = cur.fetchall()

        return {
            "database_name": db_name,
            "schema_data": {
                f"{table_schema}.{table_name}": columns
                for table_schema, table_name, columns in tables
            },
        }

    except psycopg2.Error as e:
        raise click.ClickException(f"Database error: {e}") from e
    finally:
        if "conn" in locals():
            cur.close()
            conn.close()


async def _write_file(path: Path, content: str) -> None:
    try:
        async with aiofiles.open(path, "w") as file:
            await file.write(content)
        logger.info(f"Created file: {path}")
    except OSError as exc:
        logger.error(f"Failed to write file {path}: {exc}")
        raise


class ProjectLoader:
    """Load project from YAML file."""

    def __init__(
        self,
        project_path: Path,
    ) -> None:
        self.project_path = project_path
        logger.info(f"Loading project from: {project_path}")

    def _load_project_to_dict(self) -> dict[str, Any]:
        if not self.project_path.exists():
            raise FileNotFoundError(
                f"Project config file not found: {self.project_path}",
            )

        with self.project_path.open() as stream:
            try:
                return yaml.safe_load(stream)["project"]
            except Exception as exc:
                raise exc

    def load_project(self) -> ProjectSpec:
        return ProjectSpec(**self._load_project_to_dict())

    @classmethod
    def load_project_from_db(
        cls, connection_string: str, schema: str = "public"
    ) -> ProjectSpec:
        db_info = _inspect_postgres_schema(connection_string, schema)
        db_schema: dict[str, Any] = db_info["schema_data"]
        db_name: str = db_info["database_name"]

        models = []
        for table_name_full, columns_data in db_schema.items():
            _, table_name = table_name_full.split(".")
            columns_data: list[dict[str, Any]]

            fields: list[ModelField] = []
            relationships: list[ModelRelationship] = []
            for column in columns_data:
                if "foreign_key" in column:
                    foreign_key = column.pop("foreign_key")
                    if foreign_key is not None:
                        relationship = ModelRelationship(**foreign_key)
                        relationships.append(relationship)

                        # continue, since relationships automatically
                        # converts into fields as well - to avoid duplicate field
                        continue

                data_type = FieldDataTypeEnum.from_db_type(column.pop("type"))
                column["type"] = data_type
                default = None
                extra_kwargs = None

                metadata = ModelFieldMetadata()
                if data_type == FieldDataTypeEnum.DATETIME:
                    column_name = column["name"]
                    default_timestamp = column.get("default") == "CURRENT_TIMESTAMP"
                    if default_timestamp:
                        if "create" in column_name:
                            metadata.is_created_at_timestamp = True
                            default = "datetime.now(timezone.utc)"
                        elif "update" in column_name:
                            metadata.is_updated_at_timestamp = True
                            default = "datetime.now(timezone.utc)"
                            extra_kwargs = {"onupdate": "datetime.now(timezone.utc)"}

                # temporary until any primary key name is supported
                if column["primary_key"] is True:
                    column["name"] = "id"

                field = ModelField(
                    **column,
                    metadata=metadata,
                    default_value=default,
                    extra_kwargs=extra_kwargs,
                )
                fields.append(field)

            model = Model(
                name=table_name,
                fields=fields,
                relationships=relationships,
            )
            models.append(model)

        return ProjectSpec(
            project_name=db_name,
            models=models,
            use_postgres=True,
        )


class ProjectExporter:
    """Export project to YAML file."""

    def __init__(self, project_input: ProjectSpec) -> None:
        self.project_input = project_input

    async def export_project(self) -> None:
        yaml_structure = {
            "project": self.project_input.model_dump(
                round_trip=True,  # exclude computed fields
            ),
        }
        file_path = Path.cwd() / f"{self.project_input.project_name}.yaml"
        await _write_file(
            file_path,
            yaml.dump(yaml_structure, default_flow_style=False, sort_keys=False),
        )


TEST_RENDERERS: dict[HTTPMethodEnum, Callable[[Model], str]] = {
    HTTPMethodEnum.GET: render_model_to_get_test,
    HTTPMethodEnum.GET_ID: render_model_to_get_id_test,
    HTTPMethodEnum.POST: render_model_to_post_test,
    HTTPMethodEnum.PATCH: render_model_to_patch_test,
    HTTPMethodEnum.DELETE: render_model_to_delete_test,
}


class ProjectBuilder:
    def __init__(
        self,
        project_spec: ProjectSpec,
        base_path: Path | None = None,
    ) -> None:
        self.project_spec = project_spec
        self.project_name = project_spec.project_name
        self.base_path = base_path or Path.cwd()
        self.project_dir = self.base_path / self.project_name
        self.src_dir = self.project_dir / "src"
        self._insert_relation_fields()

    def _insert_relation_fields(self) -> None:
        """Adds ModelFields to a model, based its relationships."""
        for model in self.project_spec.models:
            field_names_set = {field.name for field in model.fields}
            for relation in model.relationships:
                if relation.field_name in field_names_set:
                    continue
                model.fields.append(
                    ModelField(
                        name=relation.field_name,
                        type=FieldDataTypeEnum.UUID,
                        primary_key=False,
                        nullable=relation.nullable,
                        unique=relation.unique,
                        index=relation.index,
                        on_delete=relation.on_delete,
                        metadata=ModelFieldMetadata(is_foreign_key=True),
                    ),
                )

    async def _create_directory(self, path: Path) -> None:
        if not path.exists():
            path.mkdir(parents=True)
            logger.info(f"Created directory: {path}")

    async def _init_project_directories(self) -> None:
        await self._create_directory(self.project_dir)
        await self._create_directory(self.src_dir)

    async def _create_module_path(self, module: str) -> Path:
        path = self.src_dir / module
        await self._create_directory(path)
        return path

    async def _write_artifact(
        self,
        module: str,
        model: Model,
        render_func: Callable[[Model], str],
    ) -> None:
        path = await self._create_module_path(module)
        file_name = f"{camel_to_snake(model.name)}_{module}.py"
        await _write_file(path / file_name, render_func(model))

    async def _write_tests(self, model: Model) -> None:
        test_dir = (
            self.project_dir / "tests" / "endpoint_tests" / camel_to_snake(model.name)
        )
        await self._create_directory(test_dir)
        await _write_file(
            test_dir / "__init__.py",
            "# Automatically generated by FastAPI Forge\n",
        )

        tasks = []
        for method, render_func in TEST_RENDERERS.items():
            method_suffix = "id" if method == HTTPMethodEnum.GET_ID else ""
            file_name = (
                f"test_{method.value.replace('_id', '')}"
                f"_{camel_to_snake(model.name)}"
                f"{f'_{method_suffix}' if method_suffix else ''}"
                ".py"
            )
            tasks.append(_write_file(test_dir / file_name, render_func(model)))

        await asyncio.gather(*tasks)

    async def _write_enums(self) -> None:
        path = self.src_dir / "enums.py"
        content = render_custom_enums_to_enums(self.project_spec.custom_enums)
        await _write_file(path, content)

    async def build_artifacts(self) -> None:
        await self._init_project_directories()

        tasks = []

        if self.project_spec.custom_enums:
            tasks.append(self._write_enums())

        for model in self.project_spec.models:
            tasks.append(self._write_artifact("models", model, render_model_to_model))

            metadata = model.metadata
            if metadata.create_dtos:
                tasks.append(self._write_artifact("dtos", model, render_model_to_dto))
            if metadata.create_daos:
                tasks.append(self._write_artifact("daos", model, render_model_to_dao))
            if metadata.create_endpoints:
                tasks.append(
                    self._write_artifact("routes", model, render_model_to_routers),
                )
            if metadata.create_tests:
                tasks.append(self._write_tests(model))

        await asyncio.gather(*tasks)
