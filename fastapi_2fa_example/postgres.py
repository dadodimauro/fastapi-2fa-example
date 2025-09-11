from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, Request
from sqlalchemy import Engine, MetaData, exc
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine
from sqlalchemy.orm import Session

from .config import Settings

type ProcessName = Literal["app", "test"]
type AsyncSessionMaker = async_sessionmaker[AsyncSession]


def create_async_sessionmaker(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:  # pragma: no cover
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


def create_async_engine(process_name: ProcessName, settings: Settings) -> AsyncEngine:
    return _create_async_engine(
        url=str(settings.get_postgres_dsn("asyncpg")),
        connect_args={"server_settings": {"application_name": process_name}},
        echo=settings.DEBUG,
        pool_size=settings.POSTGRES_POOL_SIZE,
        max_overflow=settings.POSTGRES_POOL_OVERFLOW_SIZE,
        pool_recycle=settings.POSTGRES_POOL_RECYCLE_SECONDS,
        pool_timeout=settings.POSTGRES_POOL_TIMEOUT,
    )


async def get_db_sessionmaker(
    request: Request,
) -> AsyncGenerator[AsyncSessionMaker]:  # pragma: no cover
    sess_maker: AsyncSessionMaker = request.state.async_sessionmaker
    yield sess_maker


async def get_db_session(
    request: Request,
    sessionmaker: AsyncSessionMaker = Depends(get_db_sessionmaker),
) -> AsyncGenerator[AsyncSession]:  # pragma: no cover
    """
    Generates a new session for the request
    using the sessionmaker in the application state.

    Note that we store it in the request state: this way, we make sure we only have
    one session per request.

    This avoids problems with FastAPI dependency chaching mechanism.

    Ref: https://github.com/tiangolo/fastapi/discussions/8421
    """
    if session := getattr(request.state, "session", None):
        yield session
    else:
        async with get_db_session_from_pool(sessionmaker) as session:
            request.state.session = session
            yield session


@asynccontextmanager
async def get_db_session_from_pool(
    sessionmaker: AsyncSessionMaker,
) -> AsyncGenerator[AsyncSession]:  # pragma: no cover
    """
    Context manager aware db session. Will throw DbPoolExhaustedException if db pool is exhausted.
    """

    async with sessionmaker() as session:
        try:
            yield session
        except exc.TimeoutError as ex:
            await session.rollback()
            raise DbPoolExhaustedException("db pool exhaustion") from ex
        except:
            await session.rollback()
            raise
        else:
            await session.commit()


class DbPoolExhaustedException(Exception):
    message: str

    def __init__(self, message: str):  # pragma: no cover
        self.message = message


async def create_all(
    async_engine: AsyncEngine, metadata: MetaData
) -> None:  # pragma: no cover
    async with async_engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: metadata.create_all(bind=sync_conn, checkfirst=True)
        )


__all__ = [
    "AsyncSession",
    "create_async_engine",
    "get_db_session",
    "get_db_session_from_pool",
    "DbPoolExhaustedException",
    "get_db_sessionmaker",
    "AsyncSessionMaker",
    "AsyncEngine",
    "Engine",
    "Session",
    "AsyncSession",
]
