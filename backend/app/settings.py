from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def enable_local_only_defaults() -> None:
    """Disable Hugging Face Hub network checks unless an operator opts out."""
    os.environ.setdefault("HF_HUB_OFFLINE", "1")


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or a local .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="HOUSEHOLD_", extra="ignore")

    database_url: str = "sqlite:///./data/household.db"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3:4b"
    vision_model: str = "qwen2.5vl:3b"
    vision_request_timeout_seconds: float = Field(default=60.0, gt=0)
    whisper_model: str = "base"
    request_timeout_seconds: float = Field(default=30.0, gt=0)
    discovery_request_timeout_seconds: float = Field(default=90.0, gt=0)
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str = "http://127.0.0.1:8000/api/google-calendar/callback"
    google_token_encryption_key: str | None = None
    zepto_mcp_url: str = "https://mcp.zepto.co.in/mcp"
    zepto_client_id: str | None = None
    zepto_client_secret: str | None = None
    zepto_oauth_authorization_url: str | None = None
    zepto_oauth_token_url: str | None = None
    zepto_redirect_uri: str = "http://127.0.0.1:8000/api/zepto/callback"
    zepto_token_encryption_key: str | None = None
    zepto_mock_enabled: bool = False
    frontend_url: str = "http://localhost:5173"

    @property
    def database_path(self) -> Path | None:
        prefix = "sqlite:///"
        if not self.database_url.startswith(prefix) or self.database_url == "sqlite:///:memory:":
            return None
        return Path(self.database_url.removeprefix(prefix))


@lru_cache
def get_settings() -> Settings:
    return Settings()
