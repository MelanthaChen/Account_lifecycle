import json
from functools import lru_cache
from typing import Annotated, Any
from urllib.parse import urlparse

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]


class Settings(BaseSettings):
    app_name: str = "Account Intelligence Platform"
    api_v1_prefix: str = "/api/v1"
    environment: str = Field(default="local")
    database_url: str = Field(
        default="postgresql+asyncpg://account:account@localhost:55432/account_intelligence"
    )
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: DEFAULT_CORS_ORIGINS.copy(),
        validation_alias=AliasChoices("CORS_ALLOWED_ORIGINS", "CORS_ORIGINS"),
    )
    automation_workers: dict[str, str] = Field(default_factory=dict)
    automation_agent_name: str = Field(default="automation-agent")
    automation_agent_secret: str = Field(default="")
    worker_offline_seconds: int = 90

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if value is None or value == "":
            return DEFAULT_CORS_ORIGINS.copy()
        if isinstance(value, list):
            return [_normalize_origin(origin) for origin in value if str(origin).strip()]
        if isinstance(value, str):
            raw_value = value.strip()
            if raw_value.startswith("["):
                try:
                    decoded = json.loads(raw_value)
                except json.JSONDecodeError:
                    decoded = _split_origins(raw_value.strip("[]"))
                if not isinstance(decoded, list):
                    raise ValueError("CORS origins JSON value must be a list")
                return [_normalize_origin(origin) for origin in decoded if str(origin).strip()]
            return [_normalize_origin(origin) for origin in _split_origins(raw_value)]
        raise ValueError("CORS origins must be a comma-separated string or list")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def _split_origins(value: str) -> list[str]:
    return [origin.strip().strip("'\"") for origin in value.split(",") if origin.strip()]


def _normalize_origin(origin: Any) -> str:
    normalized = str(origin).strip().strip("'\"").rstrip("/")
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Invalid CORS origin: {origin}")
    return normalized
