from typing import Any, Self

from pydantic import (
    computed_field,
    model_validator,
)

from fastapi_forge.constants import TAB
from fastapi_forge.type_info_registry import TypeInfo, enum_registry
from fastapi_forge.utils.string_utils import (
    camel_to_snake,
)

from .base import BaseSchema
from .types import (
    BoundedStr,
    EnumStr,
)


class CustomEnumValue(BaseSchema):
    """Represents a single name/value pair in a custom enum."""

    name: EnumStr
    value: BoundedStr


class CustomEnum(BaseSchema):
    """Represents a custom PostgreSQL ENUM type."""

    name: EnumStr
    values: list[CustomEnumValue] = []

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        # dynamically register in the enum registry on instantiation
        enum_repr = f"enums.{self.name}"
        enum_value_repr = (
            None if not self.values else f"{enum_repr}.{self.values[0].name}"
        )
        enum_registry.register(
            self.name,
            TypeInfo(
                sqlalchemy_type=f'Enum({enum_repr}, name="{camel_to_snake(self.name)}")',
                sqlalchemy_prefix=True,
                python_type=enum_repr,
                faker_field_value=enum_value_repr,
                test_value=enum_value_repr,
            ),
        )

    @model_validator(mode="after")
    def _validate_enum(self) -> Self:
        names = [v.name for v in self.values]

        if len(names) != len(set(names)):
            raise ValueError(f"Enum '{self.name}' has duplicate names.")
        return self

    @computed_field
    @property
    def class_definition(self) -> str:
        """Returns a string representing the Python Enum class definition."""
        lines: list[str] = []
        lines.extend([f"class {self.name}(StrEnum):"])
        lines.extend([f'{TAB}"""{self.name} Enum."""\n'])

        value_lines: list[str] = []
        for v in self.values:
            value_repr = v.value if v.value == "auto()" else f'"{v.value}"'
            value_lines.extend([f"{TAB}{v.name} = {value_repr}"])

        lines.extend(value_lines)
        return "\n".join(lines)
