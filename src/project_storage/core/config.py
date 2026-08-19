from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

    APP_NAME: str = "ProjectStorage"
    API_PATH: str = "/api"
    LOG_LEVEL: Literal["debug", "info", "warning", "error", "crit"] = "warning"

    DB_URL: str

    JWT_EXPIRATION_TIME_MINUTES: int = 60
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = "not-a-production-secret-at-least-32-bytes-long"


settings = Settings()
