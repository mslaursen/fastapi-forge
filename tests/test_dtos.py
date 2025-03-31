import pytest
from pydantic import ValidationError

from fastapi_forge.dtos import Model, ModelField, ModelRelationship, ProjectSpec
from fastapi_forge.enums import FieldDataType

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
        (
            FieldDataType.FLOAT,
            'factory.Faker("pyfloat", positive=True, min_value=0.1, max_value=100)',
        ),
        (FieldDataType.BOOLEAN, 'factory.Faker("boolean")'),
        (FieldDataType.DATETIME, 'factory.Faker("date_time")'),
        (FieldDataType.UUID, None),
    ],
)
def test_factory_field_value(
    data_type: FieldDataType,
    expected_factory_value: str | None,
) -> None:
    model_field = ModelField(name="name", type=data_type)
    assert model_field.factory_field_value == expected_factory_value


###############################
# ModelRelationship DTO tests #
###############################


def test_fields() -> None:
    model_relationship = ModelRelationship(
        field_name="restaurant_id",
        target_model="restaurant",
    )
    assert model_relationship.target == "Restaurant"
    assert model_relationship.field_name_no_id == "restaurant"


def test_field_name_not_endswith_id() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ModelRelationship(
            field_name="restaurant",
            target_model="restaurant",
        )
    assert "Relationship field names must end with '_id'." in str(exc_info.value)


#########################
# ProjectSpec DTO tests #
#########################


def test_project_spec_non_existing_target_model() -> None:
    model = Model(
        name="restaurant",
        fields=[
            ModelField(name="id", type=FieldDataType.UUID, primary_key=True),
        ],
        relationships=[
            ModelRelationship(
                field_name="test_id",
                target_model="non_existing",
            ),
        ],
    )
    with pytest.raises(ValidationError) as exc_info:
        ProjectSpec(
            project_name="test_project",
            models=[model],
        )
    assert (
        "'restaurant' has a relationship to 'non_existing', which does not exist."
        in str(exc_info.value)
    )
