from typing import Annotated, Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from fastapi_forge.enums import FieldDataType
from fastapi_forge.string_utils import camel_to_snake_hyphen, snake_to_camel

BoundedStr = Annotated[str, Field(..., min_length=1, max_length=100)]
SnakeCaseStr = Annotated[BoundedStr, Field(..., pattern=r"^[a-z][a-z0-9_]*$")]
ModelName = SnakeCaseStr
FieldName = SnakeCaseStr
BackPopulates = Annotated[str, Field(..., pattern=r"^[a-z][a-z0-9_]*$")]
ProjectName = Annotated[
    BoundedStr,
    Field(..., pattern=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$"),
]


class _Base(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class ModelFieldMetadata(_Base):
    """Metadata for a model field."""

    is_created_at_timestamp: bool = False
    is_updated_at_timestamp: bool = False
    is_foreign_key: bool = False


class ModelField(_Base):
    """Represents a field in a model with validation and computed properties."""

    name: FieldName
    type: FieldDataType
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
            metadata.is_created_at_timestamp or metadata.is_updated_at_timestamp
        ) and self.type != FieldDataType.DATETIME:
            msg = "Create/update timestamp fields must be of type DateTime."
            raise ValueError(
                msg,
            )

        if metadata.is_foreign_key and self.type != FieldDataType.UUID:
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

    @computed_field
    @property
    def factory_field_value(self) -> str | dict | None:
        """Return the appropriate factory default for the model field."""
        faker_placeholder = "factory.Faker({placeholder})"

        if "email" in self.name and self.type == FieldDataType.STRING:
            return faker_placeholder.format(placeholder='"email"')

        type_to_faker = {
            FieldDataType.STRING: '"text"',
            FieldDataType.INTEGER: '"random_int"',
            FieldDataType.FLOAT: '"pyfloat", positive=True, min_value=0.1, max_value=100',
            FieldDataType.BOOLEAN: '"boolean"',
            FieldDataType.DATETIME: '"date_time"',
            FieldDataType.JSONB: {},
        }

        if self.type not in type_to_faker:
            return None

        if self.type == FieldDataType.JSONB:
            return type_to_faker[FieldDataType.JSONB]

        return faker_placeholder.format(placeholder=type_to_faker[self.type])


class ModelRelationship(_Base):
    """Represents a relationship between models."""

    field_name: FieldName
    target_model: ModelName
    back_populates: BackPopulates | None = None

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


class ModelGenerationMetadata(_Base):
    """Metadata used for code generation."""

    create_endpoints: bool = True
    create_tests: bool = True
    create_daos: bool = True
    create_dtos: bool = True


class Model(_Base):
    """Represents a model with fields and relationships."""

    name: ModelName
    fields: list[ModelField]
    relationships: list[ModelRelationship] = []
    metadata: ModelGenerationMetadata = ModelGenerationMetadata()

    @computed_field
    @property
    def name_cc(self) -> str:
        return snake_to_camel(self.name)

    @computed_field
    @property
    def name_hyphen(self) -> str:
        return camel_to_snake_hyphen(self.name)

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

        return primary_keys + other_fields + created_at + updated_at + foreign_keys

    @model_validator(mode="after")
    def _validate(self) -> Self:
        field_names = [field.name for field in self.fields]
        if len(field_names) != len(set(field_names)):
            raise ValueError(f"Model '{self.name}' contains duplicate fields.")

        if sum(field.primary_key for field in self.fields) != 1:
            raise ValueError(f"Model '{self.name}' must have exactly one primary key.")

        unque_relationships = [
            relationship.field_name for relationship in self.relationships
        ]
        if len(unque_relationships) != len(set(unque_relationships)):
            raise ValueError(
                f"Model '{self.name}' contains duplicate relationship field names.",
            )

        if sum(field.metadata.is_created_at_timestamp for field in self.fields) > 1:
            raise ValueError(
                f"Model '{self.name}' has more than one 'created_at_timestamp' fields."
            )

        if sum(field.metadata.is_updated_at_timestamp for field in self.fields) > 1:
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

        validation_rules = [
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
                    type=FieldDataType.UUID,
                    primary_key=False,
                    nullable=relation.nullable,
                    unique=relation.unique,
                    index=relation.index,
                    metadata=ModelFieldMetadata(is_foreign_key=True),
                ),
            )

        return preview_model


class ProjectSpec(_Base):
    """Represents a project specification with models and configurations."""

    project_name: ProjectName
    use_postgres: bool = False
    use_alembic: bool = False
    use_builtin_auth: bool = False
    use_redis: bool = False
    use_rabbitmq: bool = False
    models: list[Model] = []

    @model_validator(mode="after")
    def _validate_models(self) -> Self:
        model_names = [model.name for model in self.models]
        model_names_set = set(model_names)
        if len(model_names) != len(model_names_set):
            msg = "Model names must be unique."
            raise ValueError(msg)

        if self.use_alembic and not self.use_postgres:
            msg = "Cannot use Alembic if PostgreSQL is not enabled."
            raise ValueError(msg)

        if self.use_builtin_auth and not self.use_postgres:
            msg = "Cannot use built-in auth if PostgreSQL is not enabled."
            raise ValueError(msg)

        for model in self.models:
            for relationship in model.relationships:
                if relationship.target_model not in model_names_set:
                    raise ValueError(
                        f"Model '{model.name}' has a relationship to "
                        f"'{relationship.target_model}', which does not exist.",
                    )

        return self

    @model_validator(mode="after")
    def _validate_circular_references(self) -> Self:
        relationship_graph = {}

        model_names = {model.name for model in self.models}

        for model in self.models:
            relationship_graph[model.name] = [
                rel.target_model
                for rel in model.relationships
                if rel.target_model in model_names
            ]

        visited = set()
        path = set()

        def has_cycle(node):
            if node in visited:
                return False
            visited.add(node)
            path.add(node)

            for neighbor in relationship_graph.get(node, []):
                if neighbor in path or has_cycle(neighbor):
                    return True

            path.remove(node)
            return False

        for model_name in relationship_graph:
            if has_cycle(model_name):
                raise ValueError(
                    f"Circular reference detected involving model '{model_name}'. "
                    "Remove bidirectional relationships between models.",
                )

        return self
