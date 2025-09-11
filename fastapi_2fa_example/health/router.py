from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from fastapi_2fa_example.logger import logger
from fastapi_2fa_example.postgres import AsyncSession, get_db_session
from fastapi_2fa_example.redis import (
    RedisAsyncConnectionPool,
    get_redis_client_from_pool,
    get_redis_pool,
)

router = APIRouter(tags=["health"])


@router.get(
    "/healthz",
    summary="Health check",
    description="Check the health status of the application (including database and Redis).",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Service Unavailable"}
    },
)
async def healthz(
    session: AsyncSession = Depends(get_db_session),
    redis_pool: RedisAsyncConnectionPool = Depends(get_redis_pool),
) -> dict[str, str]:
    try:
        await session.execute(select(1))
        logger.debug("Database connection successful.")
    except SQLAlchemyError as e:
        logger.error("Database connection error: %s", e)
        raise HTTPException(status_code=503, detail="Database is not available") from e

    try:
        async with get_redis_client_from_pool(redis_pool) as redis:
            await redis.ping()  # pyright: ignore[reportUnknownMemberType]
            logger.debug("Redis connection successful.")
    except Exception as e:
        logger.error("Redis connection error: %s", e)
        raise HTTPException(status_code=503, detail="Redis is not available") from e

    return {"status": "ok"}
