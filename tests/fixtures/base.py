from collections.abc import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from fastapi_2fa_example.auth.dependencies import validate_access_token
from fastapi_2fa_example.auth.schemas import Token
from fastapi_2fa_example.main import app as _app
from fastapi_2fa_example.postgres import AsyncSession, get_db_session
from fastapi_2fa_example.redis import RedisAsyncConnectionPool, get_redis_pool


@pytest_asyncio.fixture
async def app(
    session: AsyncSession,
    redis_pool: RedisAsyncConnectionPool,
    request: pytest.FixtureRequest,
    access_token_fixture: Token,
) -> AsyncGenerator[FastAPI]:
    _app.dependency_overrides[get_db_session] = lambda: session
    _app.dependency_overrides[get_redis_pool] = lambda: redis_pool

    # Check if the test has the 'auth' marker
    if request.node.get_closest_marker("auth"):  # type: ignore
        _app.dependency_overrides[validate_access_token] = lambda: access_token_fixture

    yield _app

    _app.dependency_overrides.pop(get_db_session, None)
    _app.dependency_overrides.pop(get_redis_pool, None)
    _app.dependency_overrides.pop(validate_access_token, None)


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
