import pytest
from fastapi_forge.dtos import ModelField, ModelRelationship
from fastapi_forge.enums import FieldDataType
from pydantic import ValidationError

########################
# ModelField DTO tests #
########################


def test_primary_key_defaults_to_unique() -> None:
    model_field = ModelField(
        name="id",
        type=FieldDataType.UUID,
        primary_key=True,
        unique=False,
    )
    assert model_field.factory_field_value is None
    assert model_field.unique is True


def test_primary_key_cannot_be_nullable() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ModelField(
            name="id",
            type=FieldDataType.UUID,
            primary_key=True,
            nullable=True,
        )
    assert "Primary key cannot be nullable." in str(exc_info.value)


def test_primary_key_cannot_be_foreign_key() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ModelField(
            name="id",
            type=FieldDataType.UUID,
            primary_key=True,
            foreign_key="User.id",
        )
    assert "Primary key fields cannot be foreign keys." in str(exc_info.value)


@pytest.mark.parametrize(
    "invalid_name",
    [
        "InvalidName",
        "invalidName",
        "InvalidName1",
        "$invalid_name",
        "invalid_name$",
        "invalid name",
        "invalid-name",
        "1invalid_name",
    ],
)
def test_invalid_field_name(invalid_name: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        ModelField(
            name=invalid_name,
            type=FieldDataType.STRING,
        )
    assert "String should match pattern '^[a-z][a-z0-9_]*$'" in str(exc_info.value)


@pytest.mark.parametrize(
    "data_type, expected_factory_value",
    [
        (FieldDataType.STRING, 'factory.Faker("text")'),
        (FieldDataType.INTEGER, 'factory.Faker("random_int")'),
        (FieldDataType.FLOAT, 'factory.Faker("random_float")'),
        (FieldDataType.BOOLEAN, 'factory.Faker("boolean")'),
        (FieldDataType.DATETIME, 'factory.Faker("date_time")'),
        (FieldDataType.UUID, None),
    ],
)
def test_factory_field_value(
    data_type: FieldDataType, expected_factory_value: str | None
) -> None:
    model_field = ModelField(name="name", type=data_type)
    assert model_field.factory_field_value == expected_factory_value


###############################
# ModelRelationship DTO tests #
###############################


def test_fields() -> None:
    model_relationship = ModelRelationship(
        field_name="restaurant_id",
    )
    assert model_relationship.target == "Restaurant"
    assert model_relationship.target_id == "Restaurant.id"
    assert model_relationship.field_name == "restaurant_id"
    assert model_relationship.field_name_no_id == "restaurant"


def test_field_name_not_endswith_id() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ModelRelationship(
            field_name="restaurant",
        )
    assert "Relationship field names must end with '_id'." in str(exc_info.value)
