from pydantic import BaseModel, computed_field, Field, model_validator, field_validator
from typing import Annotated
from fastapi_forge.enums import FieldDataType
from typing_extensions import Self
from fastapi_forge.string_utils import snake_to_camel, camel_to_snake_hyphen


BoundedStr = Annotated[str, Field(..., min_length=1, max_length=100)]
SnakeCaseStr = Annotated[
    BoundedStr,
    Field(..., pattern=r"^[a-z][a-z0-9_]*$"),
]
ModelName = SnakeCaseStr
ModelFieldName = SnakeCaseStr
ProjectName = Annotated[
    BoundedStr,
    Field(..., pattern=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$"),
]
ForeignKey = Annotated[
    BoundedStr,
    Field(..., pattern=r"^[A-Z][a-zA-Z]*\.id$"),
]


class ModelField(BaseModel):
    """ModelField DTO."""

    name: ModelFieldName
    type: FieldDataType
    primary_key: bool = False
    nullable: bool = False
    unique: bool = False
    index: bool = False
    foreign_key: ForeignKey | None = None

    @computed_field
    @property
    def name_cc(self) -> str:
        return snake_to_camel(self.name)

    @computed_field
    @property
    def foreign_key_model(self) -> str | None:
        return snake_to_camel(self.foreign_key) if self.foreign_key else None

    @model_validator(mode="after")
    def _validate(self) -> Self:
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
    """ModelRelationship DTO."""

    field_name: str
    back_populates: str | None = None

    @field_validator("field_name")
    def _validate(cls: Self, value: str) -> str:
        if not value.endswith("_id"):
            raise ValueError("Relationship field names must endwith '_id'.")
        return value

    @computed_field
    @property
    def field_name_no_id(self) -> str:
        return self.field_name[:-3]

    @computed_field
    @property
    def target(self) -> str:
        return snake_to_camel(self.field_name)

    @computed_field
    @property
    def target_id(self) -> str:
        return f"{self.target}.id"


class Model(BaseModel):
    """Model DTO."""

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
        field_names = [field.name for field in self.fields]
        if len(field_names) != len(set(field_names)):
            raise ValueError(f"Model '{self.name}' contains duplicate fields.")

        relationship_targets = [relation.target for relation in self.relationships]
        if len(relationship_targets) != len(set(relationship_targets)):
            raise ValueError(f"Model '{self.name}' contains duplicate relationships.")

        if sum(field.primary_key for field in self.fields) != 1:
            raise ValueError(
                f"Model '{self.name}' has more or less than 1 primary key."
            )

        relationship_target_field_names = {
            relation.field_name for relation in self.relationships
        }
        for field in self.fields:
            if field.foreign_key is None:
                continue
            if field.name not in relationship_target_field_names:
                raise ValueError(
                    f"Model foreign key '{self.name}.{field.name}', "
                    f"not a relation: {relationship_target_field_names}"
                )
        return self


class ProjectSpec(BaseModel):
    """ProjectSpec DTO."""

    project_name: BoundedStr
    use_postgres: bool
    use_alembic: bool
    use_builtin_auth: bool
    use_redis: bool
    use_rabbitmq: bool
    builtin_jwt_token_expire: int | None = Field(None, ge=1, le=365)
    models: list[Model]

    @model_validator(mode="after")
    def validate_models(self) -> Self:
        """Ensure that the models are valid."""
        model_names = [model.name for model in self.models]
        if len(model_names) != len(set(model_names)):
            raise ValueError("Model names must be unique.")

        if self.use_alembic and not self.use_postgres:
            raise ValueError("Cannot use Alembic if PostgreSQL is not enabled.")

        if self.builtin_jwt_token_expire and not self.use_builtin_auth:
            raise ValueError("Cannot set JWT expiration if auth is not enabled.")

        return self


class LoadedField(BaseModel):
    name: str
    type: FieldDataType
    primary_key: bool
    foreign_key: bool
    nullable: bool
    unique: bool
    index: bool

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.foreign_key and self.type != FieldDataType.UUID:
            raise ValueError("Foreign Key fields must be UUID.")
        return self


class LoadedModel(BaseModel):
    name: str
    fields: list[LoadedField]
