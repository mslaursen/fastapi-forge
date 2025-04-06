from enum import StrEnum
from uuid import uuid4
from pydantic import BaseModel


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


# register a DataTypeInfo with a FieldDataType to make it easier to support types
class DataTypeInfo(BaseModel):

    pydantic_annotation: str
    sqlalchemy_type: str
    sqlalchemy_prefix: bool
    python_type: str
    faker_field_value: str
    value: str
    test_value: str
    test_func: str = ""


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
faker_placeholder = "factory.Faker({placeholder})"


registry.register(
    FieldDataType.STRING,
    DataTypeInfo(
        pydantic_annotation="str",
        sqlalchemy_type="String",
        sqlalchemy_prefix=True,
        python_type="str",
        faker_field_value=faker_placeholder.format(placeholder='"text"'),
        value="hello",
        test_value="'world'",
    ),
)

registry.register(
    FieldDataType.INTEGER,
    DataTypeInfo(
        pydantic_annotation="int",
        sqlalchemy_type="Integer",
        sqlalchemy_prefix=True,
        python_type="int",
        faker_field_value=faker_placeholder.format(placeholder='"random_int"'),
        value="1",
        test_value="2",
    ),
)

registry.register(
    FieldDataType.FLOAT,
    DataTypeInfo(
        pydantic_annotation="float",
        sqlalchemy_type="Float",
        sqlalchemy_prefix=True,
        python_type="float",
        faker_field_value=faker_placeholder.format(
            placeholder='"pyfloat", positive=True, min_value=0.1, max_value=100'
        ),
        value="1.0",
        test_value="2.0",
    ),
)

registry.register(
    FieldDataType.BOOLEAN,
    DataTypeInfo(
        pydantic_annotation="bool",
        sqlalchemy_type="Boolean",
        sqlalchemy_prefix=True,
        python_type="bool",
        faker_field_value=faker_placeholder.format(placeholder='"boolean"'),
        value="True",
        test_value="False",
    ),
)

registry.register(
    FieldDataType.DATETIME,
    DataTypeInfo(
        pydantic_annotation="datetime",
        sqlalchemy_type="DateTime",
        sqlalchemy_prefix=True,
        python_type="datetime",
        faker_field_value=faker_placeholder.format(placeholder='"date_time"'),
        value="datetime.now(timezone.utc)",
        test_value="datetime.now(timezone.utc)",
        test_func=".isoformat()",
    ),
)

registry.register(
    FieldDataType.UUID,
    DataTypeInfo(
        pydantic_annotation="UUID",
        sqlalchemy_type="UUID",
        sqlalchemy_prefix=False,
        python_type="UUID",
        faker_field_value=str(uuid4()),
        value=str(uuid4()),
        test_value=str(uuid4()),
    ),
)

registry.register(
    FieldDataType.JSONB,
    DataTypeInfo(
        pydantic_annotation="dict[str, Any]",
        sqlalchemy_type="JSONB",
        sqlalchemy_prefix=False,
        python_type="dict",
        faker_field_value="{}",
        value="{}",
        test_value='{"key": "value"}',
    ),
)
