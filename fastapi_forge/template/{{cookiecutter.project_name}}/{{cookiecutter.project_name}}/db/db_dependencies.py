from typing import AsyncGenerator

from sqlalchemy import exc as sa_exc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from typing import Annotated
from fastapi import Depends


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    session: AsyncSession = request.app.state.db_session_factory()

    try:
        yield session
    except sa_exc.DBAPIError:
        await session.rollback()
        raise
    finally:
        await session.commit()
        await session.close()


GetDBSession = Annotated[AsyncSession, Depends(get_db_session)]
