from sqlalchemy.ext.asyncio import create_async_engine
import sqlalchemy as sa
from src.settings import settings


async def create_test_db() -> None:
    """Create a test database."""

    engine = create_async_engine(
        str(settings.db.url.with_path("/postgres")),
        isolation_level="AUTOCOMMIT",
    )

    async with engine.begin() as conn:
        exists = await conn.scalar(
            sa.text(
                f"SELECT 1 FROM pg_database WHERE datname = '{settings.db.database}'"
            )
        )

    if exists:
        await drop_test_db()

    async with engine.connect() as conn:
        await conn.execute(
            sa.text(f'CREATE DATABASE "{settings.db.database}"'),
        )


async def drop_test_db() -> None:
    """Drop the test database, terminating all connections first."""

    engine = create_async_engine(
        str(settings.db.url.with_path("/postgres")),
        isolation_level="AUTOCOMMIT",
    )

    async with engine.connect() as conn:
        await conn.execute(
            sa.text(
                f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{settings.db.database}'
                  AND pid <> pg_backend_pid();
                """
            ),
        )

        await conn.execute(
            sa.text(f'DROP DATABASE "{settings.db.database}"'),
        )
