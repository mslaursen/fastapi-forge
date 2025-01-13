from settings import settings

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from db import meta


async def setup_db(app: FastAPI) -> None:
    """Setup database."""

    engine = create_async_engine(
        str(settings.pg.url),
        echo=settings.pg.echo,
    )
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    app.state.db_engine = engine
    app.state.db_session_factory = session_factory

    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    await engine.dispose()


async def shutdown_db(app: FastAPI) -> None:
    """Shutdown database."""

    await app.state.db_engine.dispose()
