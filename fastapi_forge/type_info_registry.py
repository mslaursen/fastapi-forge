from collections.abc import Hashable
from typing import Annotated, Any
from uuid import uuid4

from pydantic import Field
from pydantic.dataclasses import dataclass

from fastapi_forge.enums import FieldDataTypeEnum

EnumName = Annotated[str, Field(...)]


@dataclass
class TypeInfo:
    sqlalchemy_type: str
    sqlalchemy_prefix: bool
    python_type: str
    faker_field_value: str
    value: str
    test_value: str
    test_func: str = ""


class BaseRegistry[T: Hashable]:
    """Base registry class for type information."""

    def __init__(self) -> None:
        self._registry: dict[T, TypeInfo] = {}

    def register(self, key: T, data_type: TypeInfo) -> None:
        if key in self:
            raise KeyError(
                f"{self.__class__.__name__}: Key '{key}' is already registered."
            )
        self._registry[key] = data_type

    def get(self, key: T) -> TypeInfo:
        if key not in self:
            raise KeyError(f"Key '{key}' not found.")
        return self._registry[key]

    def all(self) -> list[TypeInfo]:
        return list(self._registry.values())

    def clear(self) -> None:
        self._registry.clear()

    def __contains__(self, key: Any) -> bool:
        return key in self._registry

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._registry})"


class TypeInfoRegistry(BaseRegistry[FieldDataTypeEnum]):
    """Register type info by FieldDataTypeEnum: TypeInfo."""


class EnumTypeInfoRegistry(BaseRegistry[EnumName]):
    """Register Enum type info by EnumName: TypeInfo."""


# enums are dynamically registered when a `CustomEnum` model is instantiated
# and should not be registered manually
enum_registry = EnumTypeInfoRegistry()


registry = TypeInfoRegistry()
faker_placeholder = "factory.Faker({placeholder})"

registry.register(
    FieldDataTypeEnum.STRING,
    TypeInfo(
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
    TypeInfo(
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
    TypeInfo(
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
    TypeInfo(
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
    TypeInfo(
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
    TypeInfo(
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
    TypeInfo(
        sqlalchemy_type="Integer",
        sqlalchemy_prefix=True,
        python_type="int",
        faker_field_value=faker_placeholder.format(placeholder='"random_int"'),
        value="1",
        test_value="2",
    ),
)
