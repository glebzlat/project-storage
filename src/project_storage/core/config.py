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
    JWT_SECRET_KEY: str

    UPLOAD_FILE_MAX_SIZE_B: int = 1024 ** 2 * 100  # 100 MB
    UPLOAD_FILE_CHUNK_SIZE_B: int = 1024

    AWS_S3_BUCKET_NAME: str = "project-storage"
    AWS_S3_REGION_NAME: str = "us-east-1"
    AWS_ENDPOINT_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str


settings = Settings()
