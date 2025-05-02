import redis.asyncio as redis
from fastapi import FastAPI
from {{cookiecutter.project_name}}.settings import settings


async def setup_redis(app: FastAPI) -> None:
    """Setup Redis."""
    app.state.redis = redis.Redis.from_url(
        str(settings.redis.url),
        max_connections=settings.redis.max_connections,
    )


async def shutdown_redis(app: FastAPI) -> None:
    """Shutdown Redis."""
    redis_client: redis.Redis = app.state.redis
    await redis_client.aclose()
