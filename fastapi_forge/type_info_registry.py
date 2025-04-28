from collections.abc import Hashable
from typing import Annotated, Any

from pydantic import Field
from pydantic.dataclasses import dataclass

from fastapi_forge.enums import FieldDataTypeEnum

EnumName = Annotated[str, Field(...)]


@dataclass
class TypeInfo:
    """
    Stores metadata about a database column type for testing and data generation.

    This class contains information needed to:
    - Generate SQLAlchemy column definitions
    - Create appropriate Python values for the type
    - Generate fake test data
    - Define test assertions for the type

    Attributes:
        sqlalchemy_type: The SQLAlchemy type name (e.g., 'Integer', 'String')
        sqlalchemy_prefix: Whether to prefix the `sqlalchemy_type` with 'sa.' or not.
        python_type: The corresponding Python type name (e.g., 'int', 'str')
        faker_field_value: The factory field value for this type (can be a Faker method)
        test_value: Value to insert into models for post/patch tests.
        test_func: A function to call with the `test_value`.
        encapsulate_assert: Wraps the `test_value` value (e.g, "UUID" => UUID(test_value))')

    """

    sqlalchemy_type: str
    sqlalchemy_prefix: bool
    python_type: str
    faker_field_value: str | None = None
    test_func: str | None = None
    test_value: str | None = None
    encapsulate_assert: str | None = None


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

    def remove(self, key: T) -> None:
        if key not in self:
            raise KeyError(f"Key '{key}' not found.")
        del self._registry[key]

    def update_key(self, old_key: T, new_key: T) -> None:
        if old_key not in self:
            raise KeyError(
                f"Key '{old_key}' not found. Available keys: {self._registry.keys()}"
            )
        self._registry[new_key] = self._registry.pop(old_key)

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
        faker_field_value="str(uuid4())",
        test_value="str(uuid4())",
        encapsulate_assert="UUID",
    ),
)

registry.register(
    FieldDataTypeEnum.JSONB,
    TypeInfo(
        sqlalchemy_type="JSONB",
        sqlalchemy_prefix=False,
        python_type="dict[str, Any]",
        faker_field_value="{}",
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
        test_value="2",
    ),
)
