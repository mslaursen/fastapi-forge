import pytest

from fastapi_forge.enums import FieldDataTypeEnum
from fastapi_forge.schemas import CustomEnum, CustomEnumValue
from fastapi_forge.type_info_registry import TypeInfo, TypeInfoRegistry, enum_registry

##########################
# TypeInfoRegistry tests #
##########################


def test_registry_operations(type_info_registry: TypeInfoRegistry) -> None:
    type_info_registry.register(
        FieldDataTypeEnum.STRING,
        TypeInfo(
            sqlalchemy_type="String",
            sqlalchemy_prefix=True,
            python_type="str",
        ),
    )
    assert type_info_registry.get(FieldDataTypeEnum.STRING)
    assert len(type_info_registry.all()) == 1

    assert FieldDataTypeEnum.STRING in type_info_registry

    type_info_registry.clear()
    assert len(type_info_registry.all()) == 0

    assert FieldDataTypeEnum.STRING not in type_info_registry


def test_registry_get_not_found(type_info_registry: TypeInfoRegistry) -> None:
    with pytest.raises(KeyError) as exc_info:
        type_info_registry.get(FieldDataTypeEnum.BOOLEAN)

    assert "Key 'Boolean' not found." in str(exc_info.value)


def test_key_already_registered(type_info_registry: TypeInfoRegistry) -> None:
    type_info_registry.register(
        FieldDataTypeEnum.STRING,
        TypeInfo(
            sqlalchemy_type="String",
            sqlalchemy_prefix=True,
            python_type="str",
        ),
    )
    with pytest.raises(KeyError) as exc_info:
        type_info_registry.register(
            FieldDataTypeEnum.STRING,
            TypeInfo(
                sqlalchemy_type="String",
                sqlalchemy_prefix=True,
                python_type="str",
            ),
        )
    assert "TypeInfoRegistry: Key 'String' is already registered." in str(
        exc_info.value
    )


##############################
# EnumTypeInfoRegistry tests #
##############################


def test_custom_enum_register() -> None:
    enum = CustomEnum(name="HTTPMethod")
    assert enum.name in enum_registry
    assert len(enum_registry.all()) == 1

    type_info = enum_registry.get(enum.name)
    assert type_info.sqlalchemy_type == 'Enum(enums.HTTPMethod, name="http_method")'
    assert type_info.faker_field_value is None


def test_custom_enum_register_w_values() -> None:
    enum = CustomEnum(
        name="HTTPMethod",
        values=[
            CustomEnumValue(name="GET", value="auto()"),
            CustomEnumValue(name="POST", value="auto()"),
        ],
    )

    type_info = enum_registry.get(enum.name)
    assert type_info.sqlalchemy_type == 'Enum(enums.HTTPMethod, name="http_method")'
    assert type_info.faker_field_value == "enums.HTTPMethod.GET"


def test_duplicate_custom_enum() -> None:
    CustomEnum(name="TEST")
    with pytest.raises(KeyError) as exc_info:
        CustomEnum(name="TEST")

    assert "EnumTypeInfoRegistry: Key 'TEST' is already registered." in str(
        exc_info.value
    )
