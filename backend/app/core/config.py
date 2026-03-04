"""
Application Configuration

Centralized settings using Pydantic Settings.
All secrets and toggles are read from environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Gemini API
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3-flash-preview"  # Options: "gemini-3-flash-preview", "gemini-2.0-flash", "gemini-1.5-pro"

    # API Authentication
    API_KEY: str = ""  # X-API-Key header value for frontend auth

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Module-level singleton
settings = Settings()
