import contextlib
from collections.abc import AsyncIterator
from typing import TypedDict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from fastapi_2fa_example.api import router
from fastapi_2fa_example.config import settings
from fastapi_2fa_example.health.router import router as health_router
from fastapi_2fa_example.logger import logger
from fastapi_2fa_example.models import Model
from fastapi_2fa_example.postgres import (
    AsyncEngine,
    AsyncSessionMaker,
    create_all,
    create_async_engine,
    create_async_sessionmaker,
)
from fastapi_2fa_example.redis import RedisAsyncConnectionPool, create_redis_pool


class State(TypedDict):
    async_engine: AsyncEngine
    async_sessionmaker: AsyncSessionMaker
    redis_pool: RedisAsyncConnectionPool


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    logger.info("Starting...")

    async with create_redis_pool(process_name="app") as redis_pool:
        async_engine = create_async_engine(process_name="app", settings=settings)
        async_sessionmaker = create_async_sessionmaker(async_engine)

        if settings.CREATE_TABLES:
            logger.warning("Creating database tables...")
            await create_all(async_engine=async_engine, metadata=Model.metadata)

        yield {
            "async_engine": async_engine,
            "async_sessionmaker": async_sessionmaker,
            "redis_pool": redis_pool,
        }

        logger.info("Shutting down...")
        await async_engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="2FA Example",
        description="An example FastAPI application with Two-Factor Authentication (2FA).",
        docs_url="/docs",
        lifespan=lifespan,
        contact={
            "name": "Davide Di Mauro",
            "url": "https://github.com/dadodimauro/fastapi-2fa-example",
            "email": "davide.dimauro@hotmail.it",
        },
        swagger_ui_parameters={
            "docExpansion": "none",
            "filter": "true",
            "deepLinking": "true",
            "persistAuthorization": "true",
        },
        default_response_class=JSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOWED_METHODS,
        allow_headers=settings.CORS_ALLOWED_HEADERS,
    )

    # /healthz
    app.include_router(health_router)

    app.include_router(router)

    return app


app = create_app()
