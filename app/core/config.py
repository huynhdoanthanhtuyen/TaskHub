from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "TaskHub API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    DATABASE_URL: str

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
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
