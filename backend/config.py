"""
Configuration management for WebToys platform
"""

import os
from typing import Any

from pydantic_settings import BaseSettings


def read_secret(secret_name: str) -> str | None:
    """Read a secret from the Docker secrets directory if it exists"""
    secret_path = f"/run/secrets/{secret_name}"
    if os.path.exists(secret_path):
        with open(secret_path) as f:
            return f.read().strip()
    return None


class Settings(BaseSettings):
    # API Keys
    claude_api_key: str = ""  # Default empty, will be set by read_secret or environment

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        # Handle API key that might be None
        api_key = read_secret("claude_api_key") or os.environ.get("CLAUDE_API_KEY", "")
        if api_key is not None:
            self.claude_api_key = api_key

    claude_model: str = os.environ.get("CLAUDE_MODEL", "claude-3-opus-20240229")

    # Storage
    storage_type: str = os.environ.get("STORAGE_TYPE", "file")
    storage_connection: str = os.environ.get("STORAGE_CONNECTION", "./storage")

    # Application settings
    base_url: str = os.environ.get("BASE_URL", "http://localhost:8000")
    debug: bool = os.environ.get("DEBUG", "False").lower() == "true"

    # Rate limiting
    enable_rate_limit: bool = (
        os.environ.get("ENABLE_RATE_LIMIT", "True").lower() == "true"
    )
    rate_limit_requests: int = int(os.environ.get("RATE_LIMIT_REQUESTS", "10"))
    rate_limit_window: int = int(
        os.environ.get("RATE_LIMIT_WINDOW", "3600")
    )  # 1 hour in seconds

    # Security
    cors_origins: list = os.environ.get("CORS_ORIGINS", "*").split(",")

    # Using modern Pydantic V2 config
    model_config = {"env_file": ".env"}


settings = Settings()
