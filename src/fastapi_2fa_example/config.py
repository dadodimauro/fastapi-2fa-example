from enum import Enum
from typing import Literal

from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    # Logging
    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    DEBUG: bool = True

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PWD: str = "mysecretpassword"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DATABASE: str = "postgres"
    POSTGRES_POOL_SIZE: int = 5
    POSTGRES_POOL_OVERFLOW_SIZE: int = 5
    POSTGRES_POOL_ENABLED: bool = True
    POSTGRES_SYNC_POOL_SIZE: int = 1  # Specific pool size for sync connection
    POSTGRES_POOL_RECYCLE_SECONDS: int = 600  # 10 minutes
    POSTGRES_POOL_TIMEOUT: int = (
        30  # how long to wait before failing to get a new connection
    )
    POSTGRES_LOG_LEVEL: LogLevel = LogLevel.WARNING

    # CORS
    CORS_ALLOWED_ORIGINS: list[str] = ["*"]
    CORS_ALLOWED_METHODS: list[str] = ["*"]
    CORS_ALLOWED_HEADERS: list[str] = ["*"]

    # Security
    JWT_SECRET: SecretStr = Field(default=SecretStr("changeme"))
    JWT_ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_file=".env",
        extra="allow",
    )

    def get_postgres_dsn(
        self,
        driver: Literal["asyncpg", "psycopg2"] | None,
        force_localhost: bool = False,
    ) -> str:
        return str(
            PostgresDsn.build(
                scheme=f"postgresql+{driver}" if driver else "postgresql",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PWD,
                host=self.POSTGRES_HOST if not force_localhost else "localhost",
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DATABASE,
            )
        )
