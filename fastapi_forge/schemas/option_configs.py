from typing import Self

from pydantic import (
    model_validator,
)

from .base import BaseSchema


class _BaseConfig(BaseSchema):
    """Base configuration schema for options."""

    enabled: bool = False


class PostgresConfig(_BaseConfig):
    """Configuration for the PostgreSQL."""


class AlembicConfig(_BaseConfig):
    """Configuration for the Alembic option."""


class AuthConfig(_BaseConfig):
    """Configuration for the authentication option."""

    use_builtin_auth: bool = False


class RedisConfig(_BaseConfig):
    """Configuration for the Redis option."""


class RabbitMQConfig(_BaseConfig):
    """Configuration for the RabbitMQ option."""


class TaskIQConfig(_BaseConfig):
    """Configuration for the TaskIQ option."""

    # Backends
    redis_backend: bool = False
    in_memory_backend: bool = False

    # Task queues
    rabbitmq_task_queue: bool = False
    redis_task_queue: bool = False
    sqs_task_queue: bool = False

    @model_validator(mode="after")
    def _validate(self) -> Self:
        backends = [
            self.redis_backend,
            self.in_memory_backend,
        ]

        if not backends or len(backends) > 1:
            raise ValueError(
                "TaskIQ must have exactly one backend enabled: "
                "either Redis or In-Memory."
            )

        task_queues = [
            self.rabbitmq_task_queue,
            self.redis_task_queue,
            self.sqs_task_queue,
        ]

        if not task_queues or len(task_queues) > 1:
            raise ValueError(
                "TaskIQ must have exactly one task queue enabled: "
                "either RabbitMQ, Redis, or SQS."
            )

        return self


class PrometheusConfig(_BaseConfig):
    """Configuration for the Prometheus option."""


class LogfireConfig(_BaseConfig):
    """Configuration for the Logfire option."""
