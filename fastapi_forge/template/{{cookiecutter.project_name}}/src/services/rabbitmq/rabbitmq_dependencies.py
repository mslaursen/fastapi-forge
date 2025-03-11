from fastapi import Request, Depends
from aio_pika.pool import Pool
import aio_pika
from typing import Annotated
from pydantic import BaseModel
from aio_pika import Message


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
        routing_key: str,
        message: BaseModel,
    ) -> None:
        """Publish message to a specific routing key."""

        async with self.pool.acquire() as conn:
            exchange = await conn.declare_exchange(
                name="bachelor_exchange",
                auto_delete=True,
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
            routing_key="demo_queue",
            message=payload,
        )


GetRabbitMQ = Annotated[RabbitMQService, Depends(RabbitMQService)]