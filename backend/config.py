"""
Configuration management for WebToys platform
"""

import os
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    claude_api_key: str = os.environ.get("CLAUDE_API_KEY", "")
    claude_model: str = os.environ.get("CLAUDE_MODEL", "claude-3-opus-20240229")
    
    # Storage
    storage_type: str = os.environ.get("STORAGE_TYPE", "file")
    storage_connection: str = os.environ.get("STORAGE_CONNECTION", "./storage")
    
    # Application settings
    base_url: str = os.environ.get("BASE_URL", "http://localhost:8000")
    debug: bool = os.environ.get("DEBUG", "False").lower() == "true"
    
    # Rate limiting
    enable_rate_limit: bool = os.environ.get("ENABLE_RATE_LIMIT", "True").lower() == "true"
    rate_limit_requests: int = int(os.environ.get("RATE_LIMIT_REQUESTS", "10"))
    rate_limit_window: int = int(os.environ.get("RATE_LIMIT_WINDOW", "3600"))  # 1 hour in seconds
    
    # Security
    cors_origins: list = os.environ.get("CORS_ORIGINS", "*").split(",")
    
    class Config:
        env_file = ".env"

settings = Settings() 