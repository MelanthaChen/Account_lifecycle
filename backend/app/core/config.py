from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Account Intelligence Platform"
    api_v1_prefix: str = "/api/v1"
    environment: str = Field(default="local")
    database_url: str = Field(
        default="postgresql+asyncpg://account:account@localhost:55432/account_intelligence"
    )
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
