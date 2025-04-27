from fastapi import APIRouter
from {{cookiecutter.project_name}} import exceptions
from {{cookiecutter.project_name}}.services.redis import GetRedis
{% if cookiecutter.use_rabbitmq %}
from {{cookiecutter.project_name}}.services.rabbitmq import GetRabbitMQ
{% endif %}
from pydantic import BaseModel
from typing import Any

{% if cookiecutter.use_taskiq %}
from datetime import UTC, datetime, timedelta
from {{cookiecutter.project_name}}.services.taskiq import tasks
from {{cookiecutter.project_name}}.services.taskiq.scheduler import redis_source
{% endif %}

router = APIRouter(prefix="/demo")

{% if cookiecutter.use_rabbitmq %}
class RabbitMQDemoMessage(BaseModel):
    key: str
    value: str
{% endif %}

{% if cookiecutter.use_redis %}
@router.post("/set-redis")
async def set_redis_value(key: str, value: str, redis: GetRedis,) -> None:
    await redis.set(key, value)

@router.get("/get-redis")
async def get_redis_value(key: str, redis: GetRedis,) -> dict[str, Any]:
    value = await redis.get(key)
    if value is None:
        raise exceptions.Http404(detail="Key not found in Redis")
    return {"key": key, "value": value}
{% endif %}

{% if cookiecutter.use_rabbitmq %}
@router.post("/send-rabbitmq")
async def send_rabbitmq_message(
    message: RabbitMQDemoMessage,
    rabbitmq: GetRabbitMQ,
) ->  None:
    await rabbitmq.send_demo_message(message)
{% endif %}

{% if cookiecutter.use_taskiq %}
@router.post("/taskiq-kiq")
async def kick_taskiq_message() -> None:
    await tasks.demo_task.kiq(hello="hello taskiq", world="world taskiq")


@router.post("/taskiq-scheduled")
async def schedule_taskiq_message(delay_seconds: int = 10) -> None:
    await tasks.demo_task.schedule_by_time(
        redis_source,
        datetime.now(UTC) + timedelta(seconds=delay_seconds),
        hello="hello taskiq scheduled",
        world="world taskiq scheduled",
    )
{% endif %}