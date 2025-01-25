from loguru import logger

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from src.settings import settings
from src.routes import base_router
{% if cookiecutter.use_postgres %}
from src.db import db_lifetime
{% endif %}

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan."""
    {% if cookiecutter.use_postgres %}
    await db_lifetime.setup_db(app)
    {% endif %}
    yield
    {% if cookiecutter.use_postgres %}
    await db_lifetime.shutdown_db(app)
    {% endif %}


def get_app() -> FastAPI:
    """Get FastAPI app."""

    if settings.env != "test":
        logger.info(
            settings.model_dump_json(indent=2),
        )

    app = FastAPI(lifespan=lifespan)
    app.include_router(base_router)
    return app
