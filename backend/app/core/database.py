"""
Database setup: async SQLAlchemy engine + session factory.

Concept — two layers:
  1) Engine    = a pool of connections to Postgres. Expensive to create,
                 so we make ONE and reuse it.
  2) Session   = a short-lived "workspace" for ONE request. You read/write
                 objects here, then `commit()` to save or `rollback()` on error.

The `get_db` function is a FastAPI "dependency": FastAPI calls it for each
request, gives the route the yielded session, then runs the code AFTER
`yield` (which closes the session) when the request finishes.

This means: routes never open/close connections manually — they just
declare `db: AsyncSession = Depends(get_db)` and use it.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """All ORM models inherit from this. It's the registry that lets
    SQLAlchemy know about every table. `Base.metadata` holds them all,
    which is what `create_all()` uses to make tables."""
    pass


# Create the engine ONCE. `pool_pre_ping` checks a connection is alive before
# using it (avoids "connection already closed" errors after idle time).
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_DEBUG,          # log SQL when debugging
    pool_pre_ping=True,
)

# Factory that produces sessions. `expire_on_commit=False` keeps objects
# usable after commit (so a route can still read attributes of a row it just
# saved and return them in the response).
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yield a session, close it when the request ends.

    `try/finally` guarantees cleanup even if the route raises an exception.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()   # undo any half-finished changes
            raise
