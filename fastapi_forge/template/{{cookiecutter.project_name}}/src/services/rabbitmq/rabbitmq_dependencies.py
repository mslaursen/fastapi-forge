import json
from typing import Annotated

import aio_pika
from aio_pika import ExchangeType, Message
from aio_pika.abc import AbstractChannel
from aio_pika.pool import Pool
from fastapi import Depends, Request
from loguru import logger
from pydantic import BaseModel


def get_rabbitmq_channel_pool(request: Request) -> Pool[aio_pika.Channel]:
    return request.app.state.rabbitmq_channel_pool


GetRMQChannelPool = Annotated[
    Pool[aio_pika.Channel], Depends(get_rabbitmq_channel_pool)
]


class RabbitMQService:
    """RabbitMQ Service."""

    def __init__(self, pool: GetRMQChannelPool):
        self.pool = pool

    async def _publish(
        self,
        exchange_name: str,
        routing_key: str,
        message: BaseModel,
        exchange_type: ExchangeType = ExchangeType.TOPIC,
    ) -> None:
        async with self.pool.acquire() as conn:
            exchange = await conn.declare_exchange(
                name=exchange_name,
                type=exchange_type,
                durable=True,
                auto_delete=False,
            )
            await exchange.publish(
                message=Message(
                    body=message.model_dump_json().encode("utf-8"),
                    content_encoding="utf-8",
                    content_type="application/json",
                ),
                routing_key=routing_key,
            )

    async def send_demo_message(
        self,
        payload: BaseModel,
    ) -> None:
        """Send a demo message."""
        await self._publish(
            exchange_name="demo.exchange",
            routing_key="demo.message.send",
            message=payload,
        )


GetRabbitMQ = Annotated[RabbitMQService, Depends(RabbitMQService)]


class QueueConfig(BaseModel):
    exchange_name: str
    queue_name: str
    routing_key: str
    exchange_type: ExchangeType = ExchangeType.TOPIC
    queue_durable: bool = True


async def _declare_exchange_and_queue(
    channel: AbstractChannel,
    exchange_name: str,
    queue_name: str,
    routing_key: str,
    exchange_type: ExchangeType = ExchangeType.TOPIC,
    queue_durable: bool = True,
) -> tuple[aio_pika.Exchange, aio_pika.Queue]:
    """Declare an exchange and a queue, and bind them together."""
    exchange = await channel.declare_exchange(
        name=exchange_name,
        type=exchange_type,
        durable=True,
        auto_delete=False,
    )

    queue = await channel.declare_queue(queue_name, durable=queue_durable)
    await queue.bind(exchange, routing_key=routing_key)
    return exchange, queue


async def _message_handler(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    """Handle incoming messages from RabbitMQ."""
    async with message.process():
        try:
            msg = message.body.decode()
            data = json.loads(msg)
            logger.info(f"✅ Received message: {data}")

            # handle the message here
        except Exception as e:
            logger.error(f"❌ Failed to process message: {e}")


async def init_consumer(
    channel_pool: Pool[aio_pika.Channel],
    config: QueueConfig,
) -> None:
    """Initialize a RabbitMQ consumer."""
    async with channel_pool.acquire() as channel:
        _, queue = await _declare_exchange_and_queue(
            channel,
            config.exchange_name,
            config.queue_name,
            config.routing_key,
            config.exchange_type,
            config.queue_durable,
        )

        await queue.consume(_message_handler)
        logger.info(
            f"👂 Consumer started for queue '{config.queue_name}' "
            f"with routing key '{config.routing_key}'"
        )
