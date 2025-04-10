from pydantic import create_model
from taskiq import TaskiqDepends

from src.services.rabbitmq import GetRabbitMQ
from src.services.taskiq.broker import broker


@broker.task
async def demo_task(
    hello: str,
    world: str,
    rabbitmq: GetRabbitMQ = TaskiqDepends(),
) -> None:
    await rabbitmq.send_demo_message(
        payload=create_model(
            "DemoMessage",
            hello=(str, hello),
            world=(str, world),
        )(),
    )
