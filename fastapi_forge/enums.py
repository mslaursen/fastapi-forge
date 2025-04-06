from enum import StrEnum
from typing import Any


class HTTPMethod(StrEnum):
    GET = "get"
    GET_ID = "get_id"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"


class FieldDataType(StrEnum):
    STRING = "String"
    INTEGER = "Integer"
    FLOAT = "Float"
    BOOLEAN = "Boolean"
    DATETIME = "DateTime"
    UUID = "UUID"
    JSONB = "JSONB"


class DataTypeInfo:

    def __init__(
        self,
        pydantic_annotation: str,
        sqlalchemy_type: str,
        sqlalchemy_prefix: bool,
        python_type: str,
        faker_generator: str,
        value: str,
        test_value: str,
        test_func: str,
    ):
        self.pydantic_annotation = pydantic_annotation
        self.sqlalchemy_type = sqlalchemy_type
        self.sqlalchemy_prefix = sqlalchemy_prefix
        self.python_type = python_type
        self.faker_generator = faker_generator
        self.value = value
        self.test_value = test_value
        self.test_func = test_func


class DataTypeInfoRegistry:
    def __init__(self):
        self._registry: dict[FieldDataType, DataTypeInfo] = {}

    def register(self, field_data_type: FieldDataType, data_type: DataTypeInfo):
        if field_data_type in self._registry:
            raise ValueError(f"Data type '{field_data_type}' is already registered.")
        self._registry[field_data_type] = data_type

    def get(self, field_data_type: FieldDataType) -> DataTypeInfo:
        if field_data_type not in self._registry:
            raise ValueError(f"Data type '{field_data_type}' not found.")
        return self._registry[field_data_type]

    def all(self) -> list[DataTypeInfo]:
        return list(self._registry.values())


registry = DataTypeInfoRegistry()


registry.register(
    FieldDataType.STRING,
    DataTypeInfo(
        pydantic_annotation="",
        sqlalchemy_type="String",
        sqlalchemy_prefix=False,
        python_type="str",
        faker_generator="text",
        value="hello",
        test_value='"world"',
        test_func="",
    ),
)

registry.register(
    FieldDataType.DATETIME,
    DataTypeInfo(
        pydantic_annotation="",
        sqlalchemy_type="DateTime",
        sqlalchemy_prefix=False,
        python_type="datetime",
        faker_generator="text",
        value="datetime.now(timezone.utc)",
        test_value="datetime.now(timezone.utc)",
        test_func=".isoformat()",
    ),
)
