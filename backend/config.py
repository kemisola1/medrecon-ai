"""
Application configuration for MedRecon AI.

This module centralizes environment-dependent configuration so that
application code does not directly read environment variables.

Keeping configuration in one location improves reproducibility,
testing, and deployment.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime configuration for the MedRecon backend.

    Values are loaded from environment variables or a local `.env`
    file during development.

    Secrets are intentionally never hard-coded in source code.
    """

    app_name: str = "MedRecon AI"
    app_env: str = "development"
    debug: bool = True

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    database_url: str = (
        "postgresql://medrecon:medrecon@localhost:5432/medrecon"
    )

    llm_provider: str | None = None
    llm_api_key: str | None = None

    drug_knowledge_provider: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()