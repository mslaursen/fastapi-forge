from typing import Self

from pydantic import (
    model_validator,
)

from .base import BaseSchema


class PostgresConfig(BaseSchema):
    """Configuration for the PostgreSQL."""


class AlembicConfig(BaseSchema):
    """Configuration for the Alembic option."""


class AuthConfig(BaseSchema):
    """Configuration for the authentication option."""

    use_builtin_auth: bool = False


class RedisConfig(BaseSchema):
    """Configuration for the Redis option."""


class RabbitMQConfig(BaseSchema):
    """Configuration for the RabbitMQ option."""


class TaskIQConfig(BaseSchema):
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


class PrometheusConfig(BaseSchema):
    """Configuration for the Prometheus option."""


class LogfireConfig(BaseSchema):
    """Configuration for the Logfire option."""
