"""
Application configuration using Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union


class Settings(BaseSettings):
    """Application settings."""

    # App metadata
    app_name: str = "MCP Portal API"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mcp_generator"

    # CORS - accepts either a comma-separated string or a list
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # API
    api_v1_prefix: str = "/api/v1"

    # File upload limits
    max_upload_size: int = 10 * 1024 * 1024  # 10 MB

    # Anthropic API
    anthropic_api_key: str = ""

    # OpenAI API (for OpenAI-compatible endpoints)
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"

    # AI Provider Selection
    default_ai_provider: str = "anthropic"  # "anthropic" or "openai"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
