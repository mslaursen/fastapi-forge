from fastapi import APIRouter
from src import exceptions
from src.services.redis import GetRedis
{% if cookiecutter.use_rabbitmq %}
from src.services.rabbitmq import GetRabbitMQ
{% endif %}
from pydantic import BaseModel
from typing import Any

router = APIRouter(prefix="/demo")

{% if cookiecutter.use_rabbitmq %}
class RabbitMQDemoMessage(BaseModel):
    key: str
    value: str
{% endif %}

{% if cookiecutter.use_redis %}
@router.post("/set-redis")
async def set_redis_value(key: str, value: str, redis: GetRedis,) -> dict[str, Any]:
    await redis.set(key, value)
    return {"message": "Value set successfully", "key": key, "value": value}


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
) -> dict[str, Any]:
    await rabbitmq.send_demo_message(message)
    return {
        "message": "RabbitMQ message sent successfully",
        "key": message.key,
        "value": message.value,
    }
{% endif %}