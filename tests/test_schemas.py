import pytest
from pydantic import ValidationError

from fastapi_forge.constants import TAB
from fastapi_forge.enums import FieldDataTypeEnum, OnDeleteEnum
from fastapi_forge.schemas import (
    CustomEnum,
    CustomEnumValue,
    Model,
    ModelField,
    ModelMetadata,
    ModelRelationship,
    ProjectSpec,
)

##############
# ModelField #
##############


def test_primary_key_defaults_to_unique() -> None:
    model_field = ModelField(
        name="id",
        type=FieldDataTypeEnum.UUID,
        primary_key=True,
        unique=False,
    )
    assert model_field.unique is True


def test_primary_key_cannot_be_nullable() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ModelField(
            name="id",
            type=FieldDataTypeEnum.UUID,
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
            type=FieldDataTypeEnum.STRING,
        )
    assert "String should match pattern '^[a-z][a-z0-9_]*$'" in str(exc_info.value)


@pytest.mark.parametrize(
    "data_type, expected_factory_value",
    [
        (FieldDataTypeEnum.STRING, 'factory.Faker("text")'),
        (FieldDataTypeEnum.INTEGER, 'factory.Faker("random_int")'),
        (
            FieldDataTypeEnum.FLOAT,
            'factory.Faker("pyfloat", positive=True, min_value=0.1, max_value=100)',
        ),
        (FieldDataTypeEnum.BOOLEAN, 'factory.Faker("boolean")'),
        (FieldDataTypeEnum.DATETIME, 'factory.Faker("date_time")'),
    ],
)
def test_factory_field_value(
    data_type: FieldDataTypeEnum,
    expected_factory_value: str | None,
) -> None:
    model_field = ModelField(name="name", type=data_type)
    assert model_field.type_info.faker_field_value == expected_factory_value


def test_type_missing_type_enum() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ModelField(name="test", type=FieldDataTypeEnum.ENUM)
    assert "has field type 'ENUM'" in str(exc_info.value)


def test_type_incorrect_type() -> None:
    enum = CustomEnum(
        name="Test",
        values=[
            CustomEnumValue(
                name="key",
                value="value",
            )
        ],
    )
    with pytest.raises(ValidationError) as exc_info:
        ModelField(
            name="test",
            type=FieldDataTypeEnum.STRING,
            type_enum=enum.name,
        )
    assert "but is not field type 'ENUM'" in str(exc_info.value)


#####################
# ModelRelationship #
#####################


def test_fields() -> None:
    model_relationship = ModelRelationship(
        field_name="restaurant_id",
        target_model="restaurant",
        on_delete=OnDeleteEnum.CASCADE,
    )
    assert model_relationship.target == "Restaurant"
    assert model_relationship.field_name_no_id == "restaurant"


def test_field_name_not_endswith_id() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ModelRelationship(
            field_name="restaurant",
            target_model="restaurant",
            on_delete=OnDeleteEnum.CASCADE,
        )
    assert "Relationship field names must end with '_id'." in str(exc_info.value)


##############
# CustomEnum #
##############


def test_custom_enum_not_unique_names() -> None:
    with pytest.raises(ValidationError) as exc_info:
        CustomEnum(
            name="MyEnum",
            values=[
                CustomEnumValue(name="HELLO", value="hello"),
                CustomEnumValue(name="HELLO", value="hi"),
            ],
        )
    assert "Enum 'MyEnum' has duplicate names." in str(exc_info.value)


def test_custom_enum_valid() -> None:
    enum = CustomEnum(
        name="MyEnum",
        values=[
            CustomEnumValue(name="FoO", value="foo"),
            CustomEnumValue(name="BAR", value="bar"),
            CustomEnumValue(name="BAZ", value="auto()"),
        ],
    )
    expected_definition = (
        "class MyEnum(StrEnum):\n"
        f'{TAB}"""MyEnum Enum."""\n'
        "\n"
        f'{TAB}FoO = "foo"\n'
        f'{TAB}BAR = "bar"\n'
        f"{TAB}BAZ = auto()"
    )
    assert enum.class_definition == expected_definition


###############
# ProjectSpec #
###############


def test_project_spec_non_existing_target_model() -> None:
    model = Model(
        name="restaurant",
        fields=[
            ModelField(name="id", type=FieldDataTypeEnum.UUID, primary_key=True),
        ],
        relationships=[
            ModelRelationship(
                field_name="test_id",
                target_model="non_existing",
                on_delete=OnDeleteEnum.CASCADE,
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


def test_project_spec_duplicate_model_names() -> None:
    model1 = Model(
        name="duplicate",
        fields=[ModelField(name="id", type=FieldDataTypeEnum.UUID, primary_key=True)],
    )
    model2 = Model(
        name="duplicate",
        fields=[ModelField(name="id", type=FieldDataTypeEnum.UUID, primary_key=True)],
    )
    with pytest.raises(ValidationError) as exc_info:
        ProjectSpec(
            project_name="test_project",
            models=[model1, model2],
        )
    assert "Model names must be unique." in str(exc_info.value)


def test_project_spec_invalid_enum_reference() -> None:
    model = Model(
        name="test",
        fields=[
            ModelField(name="id", type=FieldDataTypeEnum.UUID, primary_key=True),
            ModelField(
                name="status",
                type=FieldDataTypeEnum.ENUM,
                type_enum="NonExistentEnum",
            ),
        ],
    )
    with pytest.raises(ValidationError) as exc_info:
        ProjectSpec(
            project_name="test_project",
            models=[model],
            custom_enums=[CustomEnum(name="valid_enum")],
        )
    assert "Invalid enum references" in str(exc_info.value)
    assert "test.status (ref: 'NonExistentEnum')" in str(exc_info.value)
    assert "Valid enums: valid_enum" in str(exc_info.value)


def test_project_spec_multiple_auth_models() -> None:
    model1 = Model(
        name="user1",
        fields=[ModelField(name="id", type=FieldDataTypeEnum.UUID, primary_key=True)],
        metadata=ModelMetadata(is_auth_model=True),
    )
    model2 = Model(
        name="user2",
        fields=[ModelField(name="id", type=FieldDataTypeEnum.UUID, primary_key=True)],
        metadata=ModelMetadata(is_auth_model=True),
    )
    with pytest.raises(ValidationError) as exc_info:
        ProjectSpec(
            project_name="test_project",
            models=[model1, model2],
        )
    assert "Only one model can be an auth user." in str(exc_info.value)


def test_project_spec_get_auth_model() -> None:
    auth_model = Model(
        name="user",
        fields=[ModelField(name="id", type=FieldDataTypeEnum.UUID, primary_key=True)],
        metadata=ModelMetadata(is_auth_model=True),
    )
    project_spec = ProjectSpec(
        project_name="test_project",
        models=[auth_model],
        use_builtin_auth=True,
        use_postgres=True,
    )
    assert project_spec.get_auth_model() == auth_model


def test_project_spec_no_auth_model_when_not_using_auth() -> None:
    model = Model(
        name="user",
        fields=[ModelField(name="id", type=FieldDataTypeEnum.UUID, primary_key=True)],
        metadata=ModelMetadata(is_auth_model=True),
    )
    project_spec = ProjectSpec(
        project_name="test_project",
        models=[model],
        use_builtin_auth=False,
    )
    assert project_spec.get_auth_model() is None


def test_project_spec_taskiq_dependencies() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ProjectSpec(
            project_name="test_project",
            use_taskiq=True,
            use_redis=False,
            use_rabbitmq=False,
        )
    assert "TaskIQ is enabled, but the following are missing" in str(exc_info.value)
    assert "RabbitMQ" in str(exc_info.value)
    assert "Redis" in str(exc_info.value)


def test_project_spec_alembic_requires_postgres() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ProjectSpec(
            project_name="test_project",
            use_alembic=True,
            use_postgres=False,
        )
    assert "Cannot use Alembic if PostgreSQL is not enabled." in str(exc_info.value)


def test_project_spec_auth_requires_postgres() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ProjectSpec(
            project_name="test_project",
            use_builtin_auth=True,
            use_postgres=False,
        )
    assert "Cannot use built-in auth if PostgreSQL is not enabled." in str(
        exc_info.value
    )


#########
# Model #
#########


def test_model_missing_primary_key() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Model(
            name="test",
            fields=[
                ModelField(
                    name="test",
                    type=FieldDataTypeEnum.STRING,
                ),
            ],
        )
    assert "Model 'test' has no primary key defined." in str(exc_info.value)


def test_model_multiple_primary_keys() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Model(
            name="test",
            fields=[
                ModelField(
                    name="id0",
                    type=FieldDataTypeEnum.UUID,
                    primary_key=True,
                ),
                ModelField(
                    name="id1",
                    type=FieldDataTypeEnum.UUID,
                    primary_key=True,
                ),
            ],
        )
    assert "Model 'test' has multiple primary keys." in str(exc_info.value)
