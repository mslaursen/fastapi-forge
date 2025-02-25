from fastapi import APIRouter
from src import exceptions
from src.services.redis import GetRedis

router = APIRouter(prefix="/demo")

{% if cookiecutter.use_redis %}
@router.post("/set-redis")
async def set_redis_value(key: str, value: str, redis: GetRedis) -> dict[str, str]:
    await redis.set(key, value)
    return {"message": "Value set successfully", "key": key, "value": value}


@router.get("/get-redis")
async def get_redis_value(key: str, redis: GetRedis) -> dict[str, str]:
    value = await redis.get(key)
    if value is None:
        raise exceptions.Http404(detail="Key not found in Redis")
    return {"key": key, "value": value}
{% endif %}