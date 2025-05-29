from typing import Any, Self

from pydantic import (
    computed_field,
    field_validator,
    model_validator,
)

from fastapi_forge.enums import FieldDataTypeEnum, OnDeleteEnum
from fastapi_forge.type_info_registry import TypeInfo, enum_registry, registry
from fastapi_forge.utils.string_utils import (
    pluralize,
    snake_to_camel,
)

from .base import BaseSchema
from .types import (
    BackPopulates,
    EnumStr,
    FieldName,
    ModelName,
)


class ModelFieldMetadata(BaseSchema):
    """Metadata for a model field."""

    is_created_at_timestamp: bool = False
    is_updated_at_timestamp: bool = False
    is_foreign_key: bool = False


class ModelField(BaseSchema):
    """Represents a field in a model with validation and computed properties."""

    name: FieldName
    type: FieldDataTypeEnum
    type_enum: EnumStr | None = None
    primary_key: bool = False
    nullable: bool = False
    unique: bool = False
    index: bool = False
    default_value: str | None = None
    extra_kwargs: dict[str, Any] | None = None
    metadata: ModelFieldMetadata = ModelFieldMetadata()

    @computed_field
    @property
    def name_cc(self) -> str:
        """Convert field name to camelCase."""
        return snake_to_camel(self.name)

    @computed_field
    @property
    def type_info(self) -> TypeInfo:
        if self.type_enum:
            return enum_registry.get(self.type_enum)
        return registry.get(self.type)

    @model_validator(mode="after")
    def _validate_type(self) -> Self:
        if self.type == FieldDataTypeEnum.ENUM and self.type_enum is None:
            msg = (
                f"ModelField '{self.name}' has field type 'ENUM', "
                "but is missing 'type_enum'."
            )
            raise ValueError(msg)

        if self.type_enum and self.type != FieldDataTypeEnum.ENUM:
            msg = (
                f"ModelField '{self.name}' has 'type_enum' set, "
                "but is not field type 'ENUM'."
            )
            raise ValueError(msg)

        return self

    @model_validator(mode="after")
    def _validate(self) -> Self:
        """Validate field constraints."""
        if self.primary_key:
            if self.nullable:
                msg = "Primary key cannot be nullable."
                raise ValueError(msg)
            if not self.unique:
                self.unique = True

        metadata = self.metadata
        if (
            metadata.is_created_at_timestamp
            or metadata.is_updated_at_timestamp
        ) and self.type != FieldDataTypeEnum.DATETIME:
            msg = "Create/update timestamp fields must be of type DateTime."
            raise ValueError(
                msg,
            )

        if metadata.is_foreign_key and self.type != FieldDataTypeEnum.UUID:
            msg = "Foreign Keys must be of type UUID."
            raise ValueError(msg)

        if self.extra_kwargs and any(
            k == "default" for k, _ in self.extra_kwargs.items()
        ):
            msg = "The 'default' argument should be set through the default attr."
            raise ValueError(
                msg,
            )
        return self


class ModelRelationship(BaseSchema):
    """Represents a relationship between models."""

    field_name: FieldName
    target_model: ModelName
    back_populates: BackPopulates | None = None
    on_delete: OnDeleteEnum
    nullable: bool = False
    unique: bool = False
    index: bool = False

    @field_validator("field_name")
    def _validate_field_name(cls, value: str) -> str:
        """Ensure relationship field names end with '_id'."""
        if not value.endswith("_id"):
            msg = "Relationship field names must end with '_id'."
            raise ValueError(msg)
        return value

    @computed_field
    @property
    def field_name_no_id(self) -> str:
        return self.field_name[:-3]

    @computed_field
    @property
    def target(self) -> str:
        return snake_to_camel(self.target_model)


class ModelMetadata(BaseSchema):
    create_endpoints: bool = True
    create_tests: bool = True
    create_daos: bool = True
    create_dtos: bool = True
    is_auth_model: bool = False


class Model(BaseSchema):
    """Represents a model with fields and relationships."""

    name: ModelName
    fields: list[ModelField]
    relationships: list[ModelRelationship] = []
    metadata: ModelMetadata = ModelMetadata()

    @computed_field
    @property
    def name_cc(self) -> str:
        return snake_to_camel(self.name)

    @computed_field
    @property
    def name_plural(self) -> str:
        return pluralize(self.name)

    @computed_field
    @property
    def name_plural_hyphen(self) -> str:
        return self.name_plural.replace("_", "-")

    @computed_field
    @property
    def name_plural_cc(self) -> str:
        return snake_to_camel(self.name_plural)

    @computed_field
    @property
    def primary_key_fields(self) -> list[ModelField]:
        return [field for field in self.fields if field.primary_key]

    @computed_field
    @property
    def primary_key(self) -> ModelField:
        return self.primary_key_fields[0]

    @computed_field
    @property
    def is_composite(self) -> bool:
        return False

    @computed_field
    @property
    def table_args(self) -> str:
        """Returns the __table_args__ section for SQLAlchemy model."""
        if not self.is_composite:
            return ""
        args = []
        if self.is_composite:
            primary_keys = [
                f'"{field.name}"' for field in self.fields if field.primary_key
            ]
            args.append(
                f"__table_args__ = (sa.PrimaryKeyConstraint({', '.join(primary_keys)}),)"
            )
        return "\n".join(args)

    @property
    def fields_sorted(self) -> list[ModelField]:
        primary_keys = []
        other_fields = []
        created_at = []
        updated_at = []
        foreign_keys = []

        for field in self.fields:
            if field.primary_key:
                primary_keys.append(field)
            elif field.metadata.is_created_at_timestamp:
                created_at.append(field)
            elif field.metadata.is_updated_at_timestamp:
                updated_at.append(field)
            elif field.metadata.is_foreign_key:
                foreign_keys.append(field)
            else:
                other_fields.append(field)

        return (
            primary_keys
            + other_fields
            + created_at
            + updated_at
            + foreign_keys
        )

    @model_validator(mode="after")
    def _validate_primary_key(self) -> Self:
        pk_fields = self.primary_key_fields
        if not pk_fields:
            raise ValueError(
                f"Model '{self.name}' has no primary key defined. "
            )

        if len(pk_fields) > 1:
            raise ValueError(
                f"Model '{self.name}' has multiple primary keys. "
                "Currently only 1 is supported."
            )

        return self

    @model_validator(mode="after")
    def _validate(self) -> Self:
        field_names = [field.name for field in self.fields]
        if len(field_names) != len(set(field_names)):
            raise ValueError(f"Model '{self.name}' contains duplicate fields.")

        unique_relationships = [
            relationship.field_name for relationship in self.relationships
        ]
        if len(unique_relationships) != len(set(unique_relationships)):
            raise ValueError(
                f"Model '{self.name}' contains duplicate relationship field names.",
            )

        if (
            sum(
                field.metadata.is_created_at_timestamp for field in self.fields
            )
            > 1
        ):
            raise ValueError(
                f"Model '{self.name}' has more than one 'created_at_timestamp' fields."
            )

        if (
            sum(
                field.metadata.is_updated_at_timestamp for field in self.fields
            )
            > 1
        ):
            raise ValueError(
                f"Model '{self.name}' has more than one 'updated_at_timestamp' fields."
            )

        return self

    @model_validator(mode="after")
    def _validate_metadata(self) -> Self:
        create_endpoints = self.metadata.create_endpoints
        create_tests = self.metadata.create_tests
        create_daos = self.metadata.create_daos
        create_dtos = self.metadata.create_dtos

        validation_rules: list[dict[str, Any]] = [
            {
                "condition": create_endpoints,
                "dependencies": {"DAOs": create_daos, "DTOs": create_dtos},
                "error_message": f"Cannot create endpoints for model '{self.name}' because {{missing}} must be set.",
            },
            {
                "condition": create_tests,
                "dependencies": {
                    "Endpoints": create_endpoints,
                    "DAOs": create_daos,
                    "DTOs": create_dtos,
                },
                "error_message": f"Cannot create tests for model '{self.name}' because {{missing}} must be set.",
            },
            {
                "condition": create_daos,
                "dependencies": {"DTOs": create_dtos},
                "error_message": f"Cannot create DAOs for model '{self.name}' because DTOs must be set.",
            },
        ]

        for rule in validation_rules:
            if rule["condition"]:
                missing = [
                    name
                    for name, condition in rule["dependencies"].items()
                    if not condition
                ]
                if missing:
                    error_message = rule["error_message"].format(
                        missing=", ".join(missing),
                    )
                    raise ValueError(error_message)

        return self

    def get_preview(self) -> "Model":
        preview_model: Model = self.__deepcopy__()

        for relation in preview_model.relationships:
            preview_model.fields.append(
                ModelField(
                    name=relation.field_name,
                    type=FieldDataTypeEnum.UUID,
                    nullable=relation.nullable,
                    unique=relation.unique,
                    index=relation.index,
                    metadata=ModelFieldMetadata(is_foreign_key=True),
                ),
            )

        return preview_model
