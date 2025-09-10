from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Request
from redis.asyncio import BlockingConnectionPool, ConnectionError, ConnectionPool, Redis

from fastapi_2fa_example.config import settings

type RedisAsyncConnectionPool = ConnectionPool


@asynccontextmanager
async def create_redis_pool(
    process_name: str,
) -> AsyncGenerator[RedisAsyncConnectionPool]:
    redis_pool = BlockingConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        max_connections=settings.REDIS_POOL_MAX_CONNECTIONS,
        timeout=settings.REDIS_WAIT_FOR_CONNECTION_TIMEOUT,
        decode_responses=True,
        client_name=process_name,
        protocol=3,
        socket_timeout=5.0,
        socket_connect_timeout=5.0,
        health_check_interval=30,
    )
    yield redis_pool
    await redis_pool.aclose()


async def get_redis_pool(request: Request) -> RedisAsyncConnectionPool:
    return request.state.redis_pool


class RedisPoolExhaustedException(Exception):
    message: str

    def __init__(self, message: str):
        self.message = message


@asynccontextmanager
async def get_redis_client_from_pool(
    redis_pool: RedisAsyncConnectionPool,
) -> AsyncGenerator[Redis]:
    try:
        async with Redis(connection_pool=redis_pool) as client:
            yield client
    except ConnectionError as ex:
        raise RedisPoolExhaustedException("redis pool exhaustion") from ex


__all__ = [
    "RedisAsyncConnectionPool",
    "Redis",
    "create_redis_pool",
    "get_redis_pool",
    "RedisPoolExhaustedException",
    "get_redis_client_from_pool",
]
