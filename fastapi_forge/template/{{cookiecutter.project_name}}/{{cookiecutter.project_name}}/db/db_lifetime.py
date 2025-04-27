from {{cookiecutter.project_name}}.settings import settings
from {{cookiecutter.project_name}}.db import meta

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


async def setup_db(app: FastAPI) -> None:
    """Setup database."""

    engine = create_async_engine(
        str(settings.db.url),
        echo=settings.db.echo,
    )
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    app.state.db_engine = engine
    app.state.db_session_factory = session_factory

    {%- if not cookiecutter.use_alembic %}
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)
    {% endif %}
    await engine.dispose()


async def shutdown_db(app: FastAPI) -> None:
    """Shutdown database."""

    await app.state.db_engine.dispose()
