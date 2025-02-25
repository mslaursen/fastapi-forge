from fastapi import Request, Depends
import redis.asyncio as redis
from typing import AsyncGenerator, Annotated


async def get_redis(request: Request) -> AsyncGenerator[redis.Redis, None]:
    """Get Redis."""
    redis_client: redis.Redis = request.app.state.redis
    try:
        yield redis_client
    finally:
        await redis_client.aclose()


GetRedis = Annotated[redis.Redis, Depends(get_redis)]
