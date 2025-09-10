from collections.abc import AsyncGenerator, AsyncIterator

import pytest_asyncio

from fastapi_2fa_example.redis import (
    Redis,
    RedisAsyncConnectionPool,
    create_redis_pool,
    get_redis_client_from_pool,
)


@pytest_asyncio.fixture
async def redis_pool() -> AsyncGenerator[RedisAsyncConnectionPool]:
    async with create_redis_pool("test") as redis_pool:
        yield redis_pool


@pytest_asyncio.fixture
async def redis(redis_pool: RedisAsyncConnectionPool) -> AsyncGenerator[Redis]:
    async with get_redis_client_from_pool(redis_pool) as redis:
        yield redis


@pytest_asyncio.fixture(autouse=True)
async def redis_clear_all(redis_pool: RedisAsyncConnectionPool) -> AsyncIterator[None]:
    async with get_redis_client_from_pool(redis_pool) as redis:
        await redis.flushdb()  # type: ignore
    yield
