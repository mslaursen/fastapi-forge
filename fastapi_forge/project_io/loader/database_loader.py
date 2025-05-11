from typing import Any

from pydantic import ValidationError

from fastapi_forge.enums import FieldDataTypeEnum, OnDeleteEnum
from fastapi_forge.logger import logger
from fastapi_forge.schemas import (
    CustomEnum,
    CustomEnumValue,
    Model,
    ModelField,
    ModelRelationship,
    ProjectSpec,
)
from fastapi_forge.utils.string_utils import number_to_word, snake_to_camel

from ..database import DatabaseInspector, SchemaInspectionResult, SchemaInspector
from .protocols import ProjectLoader


class DatabaseProjectLoader(ProjectLoader):
    def __init__(
        self,
        inspector: DatabaseInspector,
        schema: str = "public",
    ):
        self.inspector = inspector
        self.schema = schema

    def load(self) -> ProjectSpec:
        schema_inspector = SchemaInspector(self.inspector)
        inspection_result = schema_inspector.inspect_schema(self.schema)
        return self._convert_to_project_spec(inspection_result)

    def _convert_to_project_spec(
        self, inspection: SchemaInspectionResult
    ) -> ProjectSpec:
        enum_column_lookup = {
            f"{col_info['schema']}.{col_info['table']}.{col_info['column']}": enum_type
            for enum_type, columns in inspection.enum_usage.items()
            for col_info in columns
        }

        models = []
        for table_name_full, columns_data in inspection.schema_data.items():
            _, table_name = table_name_full.split(".")
            model = self._create_model_from_table(
                table_name, table_name_full, columns_data, enum_column_lookup
            )
            models.append(model)

        custom_enums = self._create_custom_enums(inspection.enums)

        return ProjectSpec(
            project_name=inspection.database_name,
            models=models,
            custom_enums=custom_enums,
            use_postgres=True,
        )

    def _create_model_from_table(
        self,
        table_name: str,
        table_name_full: str,
        columns_data: list[dict[str, Any]],
        enum_column_lookup: dict[str, str],
    ) -> Model:
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
                self._process_column_defaults(column, data_type)
            )

            fields.append(ModelField(**column))

        return Model(name=table_name, fields=fields, relationships=relationships)

    @staticmethod
    def _process_column_defaults(
        column: dict[str, Any], data_type: Any
    ) -> tuple[str | None, dict[str, Any] | None]:
        default = None
        extra_kwargs = None

        if data_type == FieldDataTypeEnum.DATETIME:
            column_name = column["name"]
            if column.get("default") == "CURRENT_TIMESTAMP":
                default = "datetime.now(timezone.utc)"
                if "update" in column_name:
                    extra_kwargs = {"onupdate": "datetime.now(timezone.utc)"}

        return default, extra_kwargs

    def _create_custom_enums(self, db_enums: dict[str, Any]) -> list[CustomEnum]:
        custom_enums = []
        for enum_name, enum_values in db_enums.items():
            enum_name_processed = snake_to_camel(enum_name)
            custom_enum_values = self._create_enum_values(enum_values)

            custom_enum = CustomEnum(
                name=enum_name_processed, values=custom_enum_values
            )
            custom_enums.append(custom_enum)
        return custom_enums

    def _create_enum_values(self, enum_values: list[str]) -> list[CustomEnumValue]:
        custom_enum_values = []
        for value_name in enum_values:
            try:
                name = value_name
                if self._is_int_convertible(value_name):
                    name = number_to_word(value_name)

                custom_enum_values.append(CustomEnumValue(name=name, value="auto()"))
            except ValidationError:
                err_msg = f"Validation error for enum values: {enum_values}"
                logger.error(err_msg)
                # Fallback to placeholder value
                custom_enum_values = [
                    CustomEnumValue(name="placeholder", value="placeholder")
                ]
                break
        return custom_enum_values

    @staticmethod
    def _is_int_convertible(s: str) -> bool:
        try:
            int(s)
        except ValueError:
            return False
        return True
