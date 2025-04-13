from uuid import uuid4

from pydantic import BaseModel

from fastapi_forge.enums import FieldDataTypeEnum


class DataTypeInfo(BaseModel):
    sqlalchemy_type: str
    sqlalchemy_prefix: bool
    python_type: str
    faker_field_value: str
    value: str
    test_value: str
    test_func: str = ""


class DataTypeInfoRegistry:
    def __init__(self):
        self._registry: dict[FieldDataTypeEnum, DataTypeInfo] = {}

    def register(
        self,
        field_data_type: FieldDataTypeEnum,
        data_type: DataTypeInfo,
    ):
        if field_data_type in self._registry:
            raise ValueError(f"Data type '{field_data_type}' is already registered.")
        self._registry[field_data_type] = data_type

    def get(self, field_data_type: FieldDataTypeEnum) -> DataTypeInfo:
        if field_data_type not in self._registry:
            raise ValueError(f"Data type '{field_data_type}' not found.")
        return self._registry[field_data_type]

    def all(self) -> list[DataTypeInfo]:
        return list(self._registry.values())


class DataTypeInfoEnumRegistry:
    def __init__(self):
        self._registry: dict[str, DataTypeInfo] = {}

    def register(
        self,
        enum_name: str,
        data_type: DataTypeInfo,
    ):
        if enum_name in self._registry:
            raise ValueError(f"Enum '{enum_name}' is already registered.")
        self._registry[enum_name] = data_type

    def get(self, enum_name: str) -> DataTypeInfo:
        if enum_name not in self._registry:
            raise ValueError(f"Enum '{enum_name}' not found.")
        return self._registry[enum_name]

    def all(self) -> list[DataTypeInfo]:
        return list(self._registry.values())

    def __repr__(self) -> str:
        return str(list(self._registry.values()))


# enums are dynamically registered when a `CustomEnum` model is instantiated
# and should not be registered manually
enum_registry = DataTypeInfoEnumRegistry()


registry = DataTypeInfoRegistry()
faker_placeholder = "factory.Faker({placeholder})"

registry.register(
    FieldDataTypeEnum.STRING,
    DataTypeInfo(
        sqlalchemy_type="String",
        sqlalchemy_prefix=True,
        python_type="str",
        faker_field_value=faker_placeholder.format(placeholder='"text"'),
        value="hello",
        test_value="'world'",
    ),
)


registry.register(
    FieldDataTypeEnum.FLOAT,
    DataTypeInfo(
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
    FieldDataTypeEnum.BOOLEAN,
    DataTypeInfo(
        sqlalchemy_type="Boolean",
        sqlalchemy_prefix=True,
        python_type="bool",
        faker_field_value=faker_placeholder.format(placeholder='"boolean"'),
        value="True",
        test_value="False",
    ),
)

registry.register(
    FieldDataTypeEnum.DATETIME,
    DataTypeInfo(
        sqlalchemy_type="DateTime(timezone=True)",
        sqlalchemy_prefix=True,
        python_type="datetime",
        faker_field_value=faker_placeholder.format(placeholder='"date_time"'),
        value="datetime.now(timezone.utc)",
        test_value="datetime.now(timezone.utc)",
        test_func=".isoformat()",
    ),
)

registry.register(
    FieldDataTypeEnum.UUID,
    DataTypeInfo(
        sqlalchemy_type="UUID(as_uuid=True)",
        sqlalchemy_prefix=True,
        python_type="UUID",
        faker_field_value=str(uuid4()),
        value=str(uuid4()),
        test_value=str(uuid4()),
    ),
)

registry.register(
    FieldDataTypeEnum.JSONB,
    DataTypeInfo(
        sqlalchemy_type="JSONB",
        sqlalchemy_prefix=False,
        python_type="dict[str, Any]",
        faker_field_value="{}",
        value="{}",
        test_value='{"another_key": 123}',
    ),
)

registry.register(
    FieldDataTypeEnum.INTEGER,
    DataTypeInfo(
        sqlalchemy_type="Integer",
        sqlalchemy_prefix=True,
        python_type="int",
        faker_field_value=faker_placeholder.format(placeholder='"random_int"'),
        value="1",
        test_value="2",
    ),
)
