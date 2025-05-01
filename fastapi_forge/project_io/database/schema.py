from typing import Any

import psycopg2
from pydantic.dataclasses import dataclass

from fastapi_forge.logger import logger

from .protocols import DatabaseInspector


@dataclass
class SchemaInspectionResult:
    database_name: str
    schema_data: dict[str, list[dict[str, Any]]]
    enums: dict[str, list[str]]
    enum_usage: dict[str, list[dict[str, Any]]]


class SchemaInspector:
    def __init__(self, inspector: DatabaseInspector):
        self.inspector = inspector

    def inspect_schema(self, schema: str = "public") -> SchemaInspectionResult:
        logger.info(
            f"Querying database schema from: {self.inspector.get_connection_string()}"
        )
        try:
            enums = self.inspector.fetch_enums(schema)
            enum_columns = self.inspector.fetch_enum_columns(schema)
            enum_usage = self._build_enum_usage(enum_columns)
            tables = self.inspector.fetch_schema_tables(schema)

            return SchemaInspectionResult(
                database_name=self.inspector.get_db_name(),
                schema_data={
                    f"{table_schema}.{table_name}": columns
                    for table_schema, table_name, columns in tables
                },
                enums=enums,
                enum_usage=enum_usage,
            )

        except psycopg2.Error as e:
            raise ValueError(f"Database error: {e}") from e

    @staticmethod
    def _build_enum_usage(
        enum_columns: list[tuple[Any, ...]],
    ) -> dict[str, list[dict[str, Any]]]:
        usage: dict[str, list[dict[str, Any]]] = {}
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
