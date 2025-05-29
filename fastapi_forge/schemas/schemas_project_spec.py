from typing import Self

from option_configs import (
    AlembicConfig,
    AuthConfig,
    LogfireConfig,
    PostgresConfig,
    PrometheusConfig,
    RabbitMQConfig,
    RedisConfig,
    TaskIQConfig,
)
from pydantic import (
    computed_field,
    model_validator,
)

from fastapi_forge.enums import FieldDataTypeEnum

from .base import BaseSchema
from .schemas_custom_enum import CustomEnum
from .schemas_model import (
    Model,
)
from .types import (
    ProjectName,
)


class ProjectSpec(BaseSchema):
    """Represents a project specification with models and configurations."""

    project_name: ProjectName
    models: list[Model] = []
    custom_enums: list[CustomEnum] = []

    postgres_config: PostgresConfig | None = None
    alembic_config: AlembicConfig | None = None
    auth_config: AuthConfig | None = None
    redis_config: RedisConfig | None = None
    rabbitmq_config: RabbitMQConfig | None = None
    taskiq_config: TaskIQConfig | None = None
    prometheus_config: PrometheusConfig | None = None
    logfire_config: LogfireConfig | None = None

    @model_validator(mode="after")
    def _validate_enums(self) -> Self:
        valid_enum_names = {
            custom_enum.name for custom_enum in self.custom_enums
        }

        invalid_fields = [
            (model.name, field.name, field.type_enum)
            for model in self.models
            for field in model.fields
            if (
                field.type == FieldDataTypeEnum.ENUM
                and (
                    field.type_enum is None
                    or field.type_enum not in valid_enum_names
                )
            )
        ]

        if invalid_fields:
            error_lines = [
                f"• {model_name}.{field_name} (ref: '{type_enum}')"
                for model_name, field_name, type_enum in invalid_fields
            ]
            raise ValueError(
                f"Invalid enum references ({len(invalid_fields)}):\n"
                + "\n".join(error_lines)
                + f"\nValid enums: {', '.join(sorted(valid_enum_names)) or 'none'}"
            )

        return self

    @model_validator(mode="after")
    def _validate_models(self) -> Self:
        model_names = [model.name for model in self.models]
        model_names_set = set(model_names)
        if len(model_names) != len(model_names_set):
            msg = "Model names must be unique."
            raise ValueError(msg)

        enum_names = [enum.name for enum in self.custom_enums]
        if len(enum_names) != len(set(enum_names)):
            msg = "Enum names must be unique."
            raise ValueError(msg)

        if self.use_alembic and not self.use_postgres:
            msg = "Cannot use Alembic if PostgreSQL is not enabled."
            raise ValueError(msg)

        if self.use_builtin_auth and not self.use_postgres:
            msg = "Cannot use built-in auth if PostgreSQL is not enabled."
            raise ValueError(msg)

        if self.use_builtin_auth and self.get_auth_model() is None:
            msg = "Cannot use built-in auth if no auth model is defined."
            raise ValueError(msg)

        for model in self.models:
            for relationship in model.relationships:
                if relationship.target_model not in model_names_set:
                    raise ValueError(
                        f"Model '{model.name}' has a relationship to "
                        f"'{relationship.target_model}', which does not exist.",
                    )

        if sum(model.metadata.is_auth_model for model in self.models) > 1:
            msg = "Only one model can be an auth user."
            raise ValueError(msg)

        if self.use_taskiq and not (self.use_redis and self.use_rabbitmq):
            missing = []
            if not self.use_rabbitmq:
                missing.append("RabbitMQ")
            if not self.use_redis:
                missing.append("Redis")

            if missing:
                raise ValueError(
                    "TaskIQ is enabled, but the following are missing and required "
                    f"for its operation: {', '.join(missing)}."
                )

        return self

    def get_auth_model(self) -> Model | None:
        if not self.use_builtin_auth:
            return None
        for model in self.models:
            if model.metadata.is_auth_model:
                return model
        return None

    @computed_field
    @property
    def use_postgres(self) -> bool:
        return self.postgres_config is not None

    @computed_field
    @property
    def use_alembic(self) -> bool:
        return self.alembic_config is not None

    @computed_field
    @property
    def use_builtin_auth(self) -> bool:
        return (
            self.auth_config is not None and self.auth_config.use_builtin_auth
        )

    @computed_field
    @property
    def use_redis(self) -> bool:
        return self.redis_config is not None

    @computed_field
    @property
    def use_rabbitmq(self) -> bool:
        return self.rabbitmq_config is not None

    @computed_field
    @property
    def use_taskiq(self) -> bool:
        return self.taskiq_config is not None

    @computed_field
    @property
    def use_prometheus(self) -> bool:
        return self.prometheus_config is not None

    @computed_field
    @property
    def use_logfire(self) -> bool:
        return self.logfire_config is not None
