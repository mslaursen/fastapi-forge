from loguru import logger

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from src.settings import settings
from src.routes import base_router
from src.middleware import add_middleware
{% if cookiecutter.use_postgres %}
from src.db import db_lifetime
{% endif %}
{% if cookiecutter.use_redis -%}
from src.services.redis import redis_lifetime
{% endif %}
{% if cookiecutter.use_rabbitmq -%}
from src.services.rabbitmq import rabbitmq_lifetime
from src.constants import QUEUE_CONFIGS
{% endif %}
{% if cookiecutter.use_taskiq %}
from src.services.taskiq import taskiq_lifetime
{% endif %}

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan."""
    {% if cookiecutter.use_postgres %}
    await db_lifetime.setup_db(app)
    {% endif %}
    {%- if cookiecutter.use_redis -%}
    await redis_lifetime.setup_redis(app)
    {% endif %}
    {%- if cookiecutter.use_rabbitmq -%}
    await rabbitmq_lifetime.setup_rabbitmq(app, configs=QUEUE_CONFIGS)
    {% endif %}
    {%- if cookiecutter.use_taskiq %}
    await taskiq_lifetime.setup_taskiq()
    {% endif %}
    
    yield

    {% if cookiecutter.use_postgres -%}
    await db_lifetime.shutdown_db(app)
    {% endif %}
    {%- if cookiecutter.use_redis -%}
    await redis_lifetime.shutdown_redis(app)
    {% endif %}
    {%- if cookiecutter.use_rabbitmq -%}
    await rabbitmq_lifetime.shutdown_rabbitmq(app)
    {% endif %}
    {%- if cookiecutter.use_taskiq %}
    await taskiq_lifetime.shutdown_taskiq()
    {% endif %}


def get_app() -> FastAPI:
    """Get FastAPI app."""

    if settings.env != "test":
        logger.info(
            settings.model_dump_json(indent=2),
        )
    {% if cookiecutter.use_alembic %}
    logger.info("Alembic enabled - see Makefile for migration commands")
    {% endif %}
    app = FastAPI(lifespan=lifespan)
    add_middleware(app)
    app.include_router(base_router)
    return app
