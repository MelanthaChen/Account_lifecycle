from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Reddit Account Management Platform"
    api_v1_prefix: str = "/api/v1"
    environment: str = Field(default="local")
    database_url: str = Field(
        default="postgresql+asyncpg://reddit:reddit@postgres:5432/reddit_accounts"
    )
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    reddit_user_agent: str = Field(default="account-management-platform/0.1")
    sync_interval_minutes: int = Field(default=30, ge=1)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
