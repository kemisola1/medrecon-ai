"""
MedRecon AI FastAPI application.

This is the entry point for the backend HTTP application.

The initial version intentionally exposes only a health endpoint.
Business functionality will be added incrementally as individual
services and agents are implemented.
"""

from fastapi import FastAPI

from app.config import settingsS


app = FastAPI(
    title=settings.app_name,
    description=(
        "Agentic medication intelligence platform for "
        "evidence-backed medication reconciliation."
    ),
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Confirm that the MedRecon API is running.

    Returns
    -------
    dict
        A small status payload used by local development,
        automated tests, and deployment health checks.
    """

    return {
        "status": "ok",
        "service": settings.app_name,
    }