from pydantic import (
    BaseModel,
    computed_field,
    Field,
    model_validator,
    field_validator,
    ConfigDict,
)
from typing import Annotated
from fastapi_forge.enums import FieldDataType
from typing_extensions import Self
from fastapi_forge.string_utils import snake_to_camel, camel_to_snake_hyphen

BoundedStr = Annotated[str, Field(..., min_length=1, max_length=100)]
SnakeCaseStr = Annotated[BoundedStr, Field(..., pattern=r"^[a-z][a-z0-9_]*$")]
ModelName = SnakeCaseStr
FieldName = SnakeCaseStr
BackPopulates = Annotated[str, Field(..., pattern=r"^[a-z][a-z0-9_]*$")]
ProjectName = Annotated[
    BoundedStr, Field(..., pattern=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$")
]
ForeignKey = Annotated[BoundedStr, Field(..., pattern=r"^[A-Z][a-zA-Z]*\.id$")]


class ModelField(BaseModel):
    """Represents a field in a model with validation and computed properties."""

    name: FieldName
    type: FieldDataType
    primary_key: bool = False
    nullable: bool = False
    unique: bool = False
    index: bool = False
    foreign_key: ForeignKey | None = None

    @computed_field
    @property
    def name_cc(self) -> str:
        """Convert field name to camelCase."""
        return snake_to_camel(self.name)

    @computed_field
    @property
    def foreign_key_model(self) -> str | None:
        """Convert foreign key to camelCase if it exists."""
        return snake_to_camel(self.foreign_key) if self.foreign_key else None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        """Validate field constraints."""
        if self.primary_key:
            if self.foreign_key:
                raise ValueError("Primary key fields cannot be foreign keys.")
            if self.nullable:
                raise ValueError("Primary key cannot be nullable.")
            if not self.unique:
                self.unique = True
        return self

    @computed_field
    @property
    def factory_field_value(self) -> str | dict | None:
        """Return the appropriate factory default for the model field."""
        faker_placeholder = "factory.Faker({placeholder})"

        if "email" in self.name:
            return faker_placeholder.format(placeholder='"email"')

        type_to_faker = {
            FieldDataType.STRING: "text",
            FieldDataType.INTEGER: "random_int",
            FieldDataType.FLOAT: "random_float",
            FieldDataType.BOOLEAN: "boolean",
            FieldDataType.DATETIME: "date_time",
            FieldDataType.JSONB: "{}",
        }

        if self.type not in type_to_faker:
            return None

        if self.type == FieldDataType.JSONB:
            return type_to_faker[FieldDataType.JSONB]

        return faker_placeholder.format(placeholder=f'"{type_to_faker[self.type]}"')


class ModelRelationship(BaseModel):
    """Represents a relationship between models."""

    field_name: FieldName
    back_populates: BackPopulates | None = None

    @field_validator("field_name")
    def _validate_field_name(cls, value: str) -> str:
        """Ensure relationship field names end with '_id'."""
        if not value.endswith("_id"):
            raise ValueError("Relationship field names must end with '_id'.")
        return value

    @computed_field
    @property
    def field_name_no_id(self) -> str:
        """Remove '_id' suffix from the field name."""
        return self.field_name[:-3]

    @computed_field
    @property
    def target(self) -> str:
        """Convert field name to camelCase."""
        return snake_to_camel(self.field_name)

    @computed_field
    @property
    def target_id(self) -> str:
        """Return the target ID in the format 'Target.id'."""
        return f"{self.target}.id"


class Model(BaseModel):
    """Represents a model with fields and relationships."""

    name: ModelName
    fields: list[ModelField]
    relationships: list[ModelRelationship] = []

    @computed_field
    @property
    def name_cc(self) -> str:
        return snake_to_camel(self.name)

    @computed_field
    @property
    def name_hyphen(self) -> str:
        return camel_to_snake_hyphen(self.name)

    @model_validator(mode="after")
    def _validate(self) -> Self:
        """Validate model constraints."""
        field_names = [field.name for field in self.fields]
        if len(field_names) != len(set(field_names)):
            raise ValueError(f"Model '{self.name}' contains duplicate fields.")

        relationship_targets = [relation.target for relation in self.relationships]
        if len(relationship_targets) != len(set(relationship_targets)):
            raise ValueError(f"Model '{self.name}' contains duplicate relationships.")

        if sum(field.primary_key for field in self.fields) != 1:
            raise ValueError(f"Model '{self.name}' must have exactly one primary key.")

        relationship_target_field_names = {
            relation.field_name for relation in self.relationships
        }
        for field in self.fields:
            if field.foreign_key and field.name not in relationship_target_field_names:
                raise ValueError(
                    f"Model foreign key '{self.name}.{field.name}' is not a valid relationship."
                )
        return self


class ProjectSpec(BaseModel):
    """Represents a project specification with models and configurations."""

    project_name: ProjectName
    use_postgres: bool
    use_alembic: bool
    use_builtin_auth: bool
    use_redis: bool
    use_rabbitmq: bool
    models: list[Model]

    @model_validator(mode="after")
    def validate_models(self) -> Self:
        """Validate project-level constraints."""
        model_names = [model.name for model in self.models]
        if len(model_names) != len(set(model_names)):
            raise ValueError("Model names must be unique.")

        if self.use_alembic and not self.use_postgres:
            raise ValueError("Cannot use Alembic if PostgreSQL is not enabled.")

        return self


class FieldInput(BaseModel):
    """Input model for creating or updating a field."""

    model_config = ConfigDict(use_enum_values=True)

    name: FieldName
    type: FieldDataType
    primary_key: bool = False
    nullable: bool = False
    unique: bool = False
    index: bool = False
    foreign_key: bool = False
    back_populates: BackPopulates | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        """Validate field input constraints."""
        if self.foreign_key and self.type != FieldDataType.UUID:
            raise ValueError("Foreign Key fields must be UUID.")
        if not self.foreign_key and self.back_populates:
            raise ValueError("Back Populates can only be set on Foreign Keys.")
        if self.primary_key and self.foreign_key:
            raise ValueError("Primary Keys cannot be Foreign Keys.")
        if self.foreign_key and not self.name.endswith("_id"):
            raise ValueError("Foreign Key field names must end with '_id'.")
        return self


class ModelInput(BaseModel):
    """Input model for creating or updating a model."""

    name: ModelName
    fields: list[FieldInput]

    @model_validator(mode="after")
    def _validate(self) -> Self:
        """Validate model input constraints."""
        field_names = [field.name for field in self.fields]
        if len(set(field_names)) != len(field_names):
            raise ValueError("Duplicate field names are not allowed.")
        if sum(field.primary_key for field in self.fields) != 1:
            raise ValueError(f"Model '{self.name}' must have exactly one primary key.")
        return self


class ProjectInput(BaseModel):
    """Input model for creating or updating a project."""

    project_name: ProjectName
    use_postgres: bool = False
    use_alembic: bool = False
    use_builtin_auth: bool = False
    use_redis: bool = False
    use_rabbitmq: bool = False
    models: list[ModelInput] = []

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.use_alembic and not self.use_postgres:
            raise ValueError("Cannot use Alembic if PostgreSQL is not enabled.")

        model_names = [model.name for model in self.models]
        if len(model_names) != len(set(model_names)):
            raise ValueError("Model names must be unique.")

        return self
