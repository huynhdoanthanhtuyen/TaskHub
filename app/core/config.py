from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import (
    DEFAULT_CACHE_TTL_SECONDS,
    DEFAULT_REDIS_TIMEOUT_SECONDS,
)
from app.core.enums import AppEnvironment, LogLevel


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "TaskHub API"
    APP_VERSION: str = "0.1.0"

    APP_ENV: AppEnvironment = AppEnvironment.DEVELOPMENT
    DEBUG: bool = False

    # Logging
    LOG_LEVEL: LogLevel = LogLevel.INFO

    # API Documentation
    DOCS_ENABLED: bool = True

    # Database
    DATABASE_URL: str

    # Authentication
    SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        gt=0,
    )

    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        gt=0,
    )

    # Redis
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    CACHE_ENABLED: bool = True

    CACHE_TTL_SECONDS: int = Field(
        default=DEFAULT_CACHE_TTL_SECONDS,
        gt=0,
    )

    REDIS_TIMEOUT_SECONDS: float = Field(
        default=DEFAULT_REDIS_TIMEOUT_SECONDS,
        gt=0,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == AppEnvironment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        return self.APP_ENV == AppEnvironment.TESTING

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == AppEnvironment.PRODUCTION

    @model_validator(mode="after")
    def validate_production_settings(self) -> Self:
        if self.is_production and self.DEBUG:
            raise ValueError("DEBUG must be disabled in production")

        return self


settings = Settings()
