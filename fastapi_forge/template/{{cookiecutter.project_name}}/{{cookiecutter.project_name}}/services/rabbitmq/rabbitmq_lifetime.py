import aio_pika
from aio_pika.abc import AbstractChannel, AbstractRobustConnection
from aio_pika.pool import Pool
from fastapi import FastAPI

from {{cookiecutter.project_name}}.services.rabbitmq.rabbitmq_dependencies import QueueConfig, init_consumer
from {{cookiecutter.project_name}}.settings import settings


async def setup_rabbitmq(
    app: FastAPI,
    configs: list[QueueConfig],
) -> None:
    """Setup RabbitMQ."""

    async def get_connection() -> AbstractRobustConnection:
        return await aio_pika.connect_robust(settings.rabbitmq.url)

    connection_pool: Pool[AbstractRobustConnection] = Pool(
        get_connection, max_size=settings.rabbitmq.connection_pool_size
    )

    async def get_channel() -> AbstractChannel:
        async with connection_pool.acquire() as connection:
            return await connection.channel()

    channel_pool: Pool[aio_pika.Channel] = Pool(get_channel, max_size=settings.rabbitmq.channel_pool_size)

    for config in configs:
        await init_consumer(channel_pool, config)

    app.state.rabbitmq_connection_pool = connection_pool
    app.state.rabbitmq_channel_pool = channel_pool


async def shutdown_rabbitmq(app: FastAPI) -> None:
    await app.state.rabbitmq_channel_pool.close()
    await app.state.rabbitmq_connection_pool.close()
