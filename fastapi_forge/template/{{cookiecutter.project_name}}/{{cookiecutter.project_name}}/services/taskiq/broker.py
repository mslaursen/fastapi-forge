from typing import Any
import taskiq_fastapi
from taskiq import AsyncBroker, InMemoryBroker
from taskiq.serializers import ORJSONSerializer
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from {{cookiecutter.project_name}}.settings import settings

broker: AsyncBroker

if settings.env == "test":
    broker = InMemoryBroker(await_inplace=True)
else:
    result_backend: RedisAsyncResultBackend[Any] = RedisAsyncResultBackend(str(settings.redis.url))
    broker = AioPikaBroker(
        str(settings.rabbitmq.url),
    ).with_result_backend(result_backend)
    broker.with_serializer(ORJSONSerializer())

taskiq_fastapi.init(broker, "{{cookiecutter.project_name}}.main:get_app")
