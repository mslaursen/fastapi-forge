from fastapi import FastAPI
import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractChannel
from aio_pika.pool import Pool
from src.settings import settings


async def setup_rabbitmq(app: FastAPI) -> None:
    """Setup RabbitMQ,"""

    async def get_connection() -> AbstractRobustConnection:
        return await aio_pika.connect_robust(settings.rabbitmq.url)

    connection_pool: Pool[AbstractRobustConnection] = Pool(
        get_connection, max_size=settings.rabbitmq.connection_pool_size
    )

    async def get_channel() -> AbstractChannel:
        async with connection_pool.acquire() as connection:
            return await connection.channel()

    channel_pool: Pool[aio_pika.Channel] = Pool(
        get_channel, max_size=settings.rabbitmq.channel_pool_size
    )

    app.state.rabbitmq_connection_pool = connection_pool
    app.state.rabbitmq_channel_pool = channel_pool


async def shutdown_rabbitmq(app: FastAPI) -> None:
    """Shutdown RabbitMQ."""

    await app.state.rabbitmq_channel_pool.close()
    await app.state.rabbitmq_connection_pool.close()