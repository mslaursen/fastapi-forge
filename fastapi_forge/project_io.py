import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import aiofiles
import psycopg2
import yaml
from pydantic import ValidationError

from fastapi_forge.dtos import (
    CustomEnum,
    CustomEnumValue,
    Model,
    ModelField,
    ModelFieldMetadata,
    ModelRelationship,
    ProjectSpec,
)
from fastapi_forge.enums import FieldDataTypeEnum, HTTPMethodEnum, OnDeleteEnum
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
from fastapi_forge.string_utils import camel_to_snake, number_to_word, snake_to_camel


def _validate_connection_string(connection_string: str) -> str:
    parsed = urlparse(connection_string)
    if parsed.scheme != "postgresql":
        msg = "Connection string must start with 'postgresql://'"
        raise ValueError(msg)

    db_name = parsed.path[1:]
    if not db_name:
        msg = "Database name not found in connection string"
        raise ValueError(msg)
    return db_name


def _fetch_enums(cursor, schema: str) -> dict[str, list[str]]:
    cursor.execute(
        """
        SELECT t.typname AS enum_name,
               array_agg(e.enumlabel ORDER BY e.enumsortorder) AS enum_values
        FROM pg_catalog.pg_type t
        JOIN pg_catalog.pg_enum e ON t.oid = e.enumtypid
        WHERE t.typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s)
        GROUP BY t.typname;
    """,
        (schema,),
    )
    return dict(cursor.fetchall())


def _fetch_enum_columns(cursor, schema: str) -> list[tuple]:
    cursor.execute(
        """
        SELECT
            c.table_schema,
            c.table_name,
            c.column_name,
            format_type(a.atttypid, a.atttypmod) AS data_type,
            t.typname AS enum_type
        FROM pg_catalog.pg_attribute a
        JOIN pg_catalog.pg_class cl ON a.attrelid = cl.oid
        JOIN pg_catalog.pg_namespace n ON cl.relnamespace = n.oid
        JOIN pg_catalog.pg_type t ON a.atttypid = t.oid
        JOIN information_schema.columns c ON
            c.table_schema = n.nspname AND
            c.table_name = cl.relname AND
            c.column_name = a.attname
        WHERE n.nspname = %s AND
              t.typtype = 'e' AND
              a.attnum > 0 AND
              NOT a.attisdropped
        ORDER BY c.table_schema, c.table_name, c.column_name;
    """,
        (schema,),
    )
    return cursor.fetchall()


def _build_enum_usage(enum_columns: list[tuple]) -> dict[str, list[dict[str, Any]]]:
    usage = {}
    for schema, table, column, data_type, enum_type in enum_columns:
        if enum_type not in usage:
            usage[enum_type] = []
        usage[enum_type].append(
            {
                "schema": schema,
                "table": table,
                "column": column,
                "data_type": data_type,
            }
        )
    return usage


def _fetch_schema_tables(cursor, schema: str) -> list[tuple]:
    cursor.execute(
        """
        SELECT
            c.table_schema,
            c.table_name,
            json_agg(
                json_build_object(
                    'name', c.column_name,
                    'type', c.data_type,
                    'nullable', c.is_nullable = 'YES',
                    'primary_key', pk.column_name IS NOT NULL,
                    'unique', uq.column_name IS NOT NULL,
                    'default', null,
                    'foreign_key',
                        CASE WHEN fk_ref.foreign_table_name IS NOT NULL THEN
                            json_build_object(
                                'field_name', c.column_name,
                                'target_model', fk_ref.foreign_table_name,
                                'referenced_field', fk_ref.foreign_column_name
                            )
                        ELSE NULL END
                ) ORDER BY c.ordinal_position
            ) AS columns
        FROM information_schema.columns c
        LEFT JOIN (
            SELECT kcu.table_schema, kcu.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
                AND tc.table_name = kcu.table_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
        ) pk ON c.table_schema = pk.table_schema AND c.table_name = pk.table_name
            AND c.column_name = pk.column_name
        LEFT JOIN (
            SELECT kcu.table_schema, kcu.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
                AND tc.table_name = kcu.table_name
            WHERE tc.constraint_type = 'UNIQUE'
              AND tc.constraint_name NOT IN (
                  SELECT constraint_name
                  FROM information_schema.table_constraints
                  WHERE constraint_type = 'PRIMARY KEY'
              )
        ) uq ON c.table_schema = uq.table_schema
            AND c.table_name = uq.table_name
            AND c.column_name = uq.column_name
        LEFT JOIN (
            SELECT kcu.table_schema, kcu.table_name, kcu.column_name,
                   ccu.table_schema AS foreign_table_schema,
                   ccu.table_name AS foreign_table_name,
                   ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
                AND tc.table_name = kcu.table_name
            JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
                AND tc.table_schema = ccu.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
        ) fk_ref ON c.table_schema = fk_ref.table_schema
            AND c.table_name = fk_ref.table_name AND c.column_name = fk_ref.column_name
        WHERE c.table_schema = %s
        GROUP BY c.table_schema, c.table_name
        ORDER BY c.table_schema, c.table_name;
    """,
        (schema,),
    )
    return cursor.fetchall()


def _process_column_defaults(column: dict[str, Any], data_type: Any) -> tuple:
    default = None
    extra_kwargs = None

    if data_type == FieldDataTypeEnum.DATETIME:
        column_name = column["name"]
        if column.get("default") == "CURRENT_TIMESTAMP":
            default = "datetime.now(timezone.utc)"
            if "update" in column_name:
                extra_kwargs = {"onupdate": "datetime.now(timezone.utc)"}

    return default, extra_kwargs


def _inspect_postgres_schema(
    connection_string: str, schema: str = "public"
) -> dict[str, Any]:
    logger.info(f"Querying database schema from: {connection_string}")
    try:
        db_name = _validate_connection_string(connection_string)
        with psycopg2.connect(connection_string) as conn, conn.cursor() as cur:
            enums = _fetch_enums(cur, schema)
            enum_columns = _fetch_enum_columns(cur, schema)
            enum_usage = _build_enum_usage(enum_columns)
            tables = _fetch_schema_tables(cur, schema)

            return {
                "database_name": db_name,
                "schema_data": {
                    f"{table_schema}.{table_name}": columns
                    for table_schema, table_name, columns in tables
                },
                "enums": enums,
                "enum_usage": enum_usage,
            }

    except psycopg2.Error as e:
        raise ValueError(f"Database error: {e}") from e


async def _write_file(path: Path, content: str) -> None:
    try:
        async with aiofiles.open(path, "w") as file:
            await file.write(content)
        logger.info(f"Created file: {path}")
    except OSError:
        logger.error(f"Failed to write file {path}")
        raise


class ProjectLoader:
    def __init__(self, project_path: Path) -> None:
        self.project_path = project_path
        logger.info(f"Loading project from: {project_path}")

    def _load_project_to_dict(self) -> dict[str, Any]:
        if not self.project_path.exists():
            raise FileNotFoundError(
                f"Project config file not found: {self.project_path}"
            )

        with self.project_path.open() as stream:
            return yaml.safe_load(stream)["project"]

    def load(self) -> ProjectSpec:
        return ProjectSpec(**self._load_project_to_dict())

    @classmethod
    def load_from_conn_string(
        cls, conn_string: str, schema: str = "public"
    ) -> ProjectSpec:
        db_info = _inspect_postgres_schema(conn_string, schema)
        db_name = db_info["database_name"]
        db_schema: dict[str, Any] = db_info["schema_data"]
        db_enums: dict[str, Any] = db_info["enums"]
        db_enum_usage: dict[str, Any] = db_info["enum_usage"]

        enum_column_lookup = {
            f"{col_info['schema']}.{col_info['table']}.{col_info['column']}": enum_type
            for enum_type, columns in db_enum_usage.items()
            for col_info in columns
        }

        models = []
        for table_name_full, columns_data in db_schema.items():
            _, table_name = table_name_full.split(".")

            fields = []
            relationships = []
            for column in columns_data:
                if column.get("foreign_key"):
                    relationships.append(
                        ModelRelationship(
                            **column["foreign_key"], on_delete=OnDeleteEnum.CASCADE
                        )
                    )
                    continue

                column_key = f"{table_name_full}.{column['name']}"
                enum_type = enum_column_lookup.get(column_key)
                data_type = (
                    FieldDataTypeEnum.ENUM
                    if enum_type
                    else FieldDataTypeEnum.from_db_type(column["type"])
                )

                if enum_type:
                    column["type_enum"] = snake_to_camel(enum_type)

                column["type"] = data_type
                column["default_value"], column["extra_kwargs"] = (
                    _process_column_defaults(column, data_type)
                )

                if column["primary_key"]:
                    column["name"] = "id"

                fields.append(ModelField(**column))

            models.append(
                Model(name=table_name, fields=fields, relationships=relationships)
            )

        def _is_int_convertible(s: str) -> bool:
            try:
                int(s)
            except ValueError:
                return False
            return True

        custom_enums = []
        for enum_name, enum_values in db_enums.items():
            enum_name_processed = snake_to_camel(enum_name)

            custom_enum_values = []
            for value_name in enum_values:
                name = value_name
                try:
                    if _is_int_convertible(value_name):
                        name = number_to_word(value_name)

                    custom_enum_value = CustomEnumValue(
                        name=name,
                        value="auto()",
                    )
                    custom_enum_values.append(custom_enum_value)
                except ValidationError:
                    err_msg = (
                        f"Validation error for CustomEnum '{enum_name_processed}', "
                        f"having name labels: {enum_values}"
                    )
                    logger.error(err_msg)
                    # to avoid errors where an enum column may be not nullable
                    custom_enum_values = [
                        CustomEnumValue(
                            name="placeholder",
                            value="placeholder",
                        )
                    ]
                    break

            custom_enum = CustomEnum(
                name=enum_name_processed, values=custom_enum_values
            )
            custom_enums.append(custom_enum)

        return ProjectSpec(
            project_name=db_name,
            models=models,
            custom_enums=custom_enums,
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
