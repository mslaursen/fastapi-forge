from pydantic import BaseModel, computed_field, Field, model_validator
from typing import Annotated
from fastapi_forge.enums import FieldType
from typing_extensions import Self

NonEmptyStr = Annotated[str, Field(..., min_length=1)]


class ModelField(BaseModel):
    """ModelField DTO."""

    name: NonEmptyStr
    type: FieldType
    primary_key: bool = False
    nullable: bool = False
    unique: bool = False
    index: bool = False
    foreign_key: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_foreign_key(self) -> Self:
        """Ensure that the foreign key is valid."""
        if self.foreign_key and self.primary_key:
            raise ValueError("Primary key fields cannot be foreign keys.")

        if self.foreign_key and self.type != FieldType.UUID:
            raise ValueError("Foreign key fields must be of type UUID.")

        if self.foreign_key and self.foreign_key.count(".") != 1:
            raise ValueError("Foreign key must be in the format 'Model.field'.")

        if self.foreign_key and self.foreign_key.split(".")[1] != "id":
            raise ValueError(
                "Foreign key must reference the primary key of the target model."
            )

        if self.foreign_key and self.foreign_key.split(".")[0] == self.name:
            raise ValueError("Foreign key cannot reference the same model field")

        return self

    @computed_field
    @property
    def factory_field_value(self) -> str | None:
        """Return the appropriate factory default for the model field."""

        faker_placeholder = "factory.Faker({placeholder})"

        if "email" in self.name:
            return faker_placeholder.format(placeholder='"email"')

        type_to_faker = {
            FieldType.STRING: '"text"',
            FieldType.INTEGER: '"random_int"',
            FieldType.FLOAT: '"random_float"',
            FieldType.BOOLEAN: '"boolean"',
            FieldType.DATETIME: '"date_time"',
        }

        if self.type not in type_to_faker:
            return None

        return faker_placeholder.format(placeholder=type_to_faker[self.type])


class ModelRelationship(BaseModel):
    """ModelRelationship DTO."""

    type: str
    target: str
    foreign_key: str


class Model(BaseModel):
    """Model DTO."""

    name: str
    fields: list[ModelField]
    relationships: list[ModelRelationship] = []


class ProjectSpec(BaseModel):
    """ProjectSpec DTO."""

    project_name: str
    use_postgres: bool
    use_alembic: bool
    use_builtin_auth: bool
    builtin_jwt_token_expire: int
    create_daos: bool
    create_routes: bool
    create_tests: bool
    models: list[Model]
