import uuid
from collections.abc import AsyncIterator, Callable, Coroutine
from uuid import UUID

import pytest_asyncio
from pydantic_core import Url
from sqlalchemy import Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import (  # type: ignore
    create_database,  # type: ignore
    database_exists,  # type: ignore
    drop_database,  # type: ignore
)

from fastapi_2fa_example.config import settings
from fastapi_2fa_example.models import Model
from fastapi_2fa_example.postgres import AsyncSession, create_async_engine


class TestModel(Model):
    __test__ = False  # This is a base class, not a test

    __tablename__ = "test_model"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=None)
    uuid: Mapped[UUID] = mapped_column(Uuid, default=uuid.uuid4)
    int_column: Mapped[int | None] = mapped_column(Integer, default=None, nullable=True)
    str_column: Mapped[str | None] = mapped_column(String, default=None, nullable=True)


def get_database_url(driver: str = "asyncpg") -> str:
    return str(
        Url.build(
            scheme=f"postgresql+{driver}",
            username=settings.POSTGRES_USER,
            password=settings.POSTGRES_PWD,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            path=settings.POSTGRES_DATABASE,
        )
    )


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def initialize_test_database() -> AsyncIterator[None]:
    sync_database_url = get_database_url("psycopg2")

    if database_exists(sync_database_url):
        drop_database(sync_database_url)

    create_database(sync_database_url)

    engine = create_async_engine(
        process_name="test",
        settings=settings,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

        # crearte a session to create the test model
        session = AsyncSession(bind=conn, expire_on_commit=False)
        await session.close()

    await engine.dispose()

    yield

    drop_database(sync_database_url)


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(
        process_name="test",
        settings=settings,
    )
    connection = await engine.connect()
    transaction = await connection.begin()

    session = AsyncSession(bind=connection, expire_on_commit=False)

    yield session

    await transaction.rollback()
    await connection.close()
    await engine.dispose()


SaveFixture = Callable[[Model], Coroutine[None, None, None]]
RefreshFixture = Callable[[Model], Coroutine[None, None, None]]


def save_fixture_factory(session: AsyncSession) -> SaveFixture:
    async def _save_fixture(model: Model) -> None:
        session.add(model)
        await session.flush()
        await session.refresh(model)

    return _save_fixture


@pytest_asyncio.fixture
async def save_fixture(session: AsyncSession) -> SaveFixture:
    return save_fixture_factory(session)


def refresh_fixture_factory(session: AsyncSession) -> RefreshFixture:
    async def _refresh_fixture(model: Model) -> None:
        await session.refresh(model)

    return _refresh_fixture


@pytest_asyncio.fixture
async def refresh_fixture(session: AsyncSession) -> RefreshFixture:
    return refresh_fixture_factory(session)
