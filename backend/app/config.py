"""
Application configuration for MedRecon AI.

This module centralizes application configuration so that the rest
of the application does not need to read environment variables
directly.

Configuration values can come from environment variables or from
a local .env file during development.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime configuration for the MedRecon AI backend.

    Keeping configuration in a dedicated class makes the application
    easier to configure, test, and deploy across different environments.

    Secrets such as API keys are loaded from environment variables
    rather than being hard-coded into the source code.
    """

    # Basic application information
    app_name: str = "MedRecon AI"
    app_env: str = "development"
    debug: bool = True

    # Backend server configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # Database configuration
    database_url: str = "sqlite:///./medrecon.db"
    
    # AI/LLM configuration
    llm_provider: str | None = None
    llm_api_key: str | None = None

    # Medication knowledge source configuration
    drug_knowledge_provider: str | None = None

    # Configuration loading behavior
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Create one shared configuration object for the application.
#
# Other modules can import this as:
#
#     from app.config import settings
#
settings = Settings()