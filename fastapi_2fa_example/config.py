import os
from enum import Enum, StrEnum
from typing import Literal

from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    development = "development"
    testing = "testing"
    staging = "staging"
    production = "production"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


env = Environment(os.getenv("ENV", Environment.development))
env_file = ".env.testing" if env == Environment.testing else ".env"


class Settings(BaseSettings):
    ENV: Environment = Environment.development

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

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_POOL_MAX_CONNECTIONS: int = 200
    REDIS_WAIT_FOR_CONNECTION_TIMEOUT: int = 2  # seconds

    # CORS
    CORS_ALLOWED_ORIGINS: list[str] = ["*"]
    CORS_ALLOWED_METHODS: list[str] = ["*"]
    CORS_ALLOWED_HEADERS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # Security
    JWT_SECRET: SecretStr = Field(default=SecretStr("changeme"))
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    LOGIN_TOKEN_EXPIRE_MINUTES: int = 10
    OTP_EXPIRE_MINUTES: int = 5

    # Other
    CREATE_TABLES: bool = False

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_file=env_file,
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


settings = Settings()
