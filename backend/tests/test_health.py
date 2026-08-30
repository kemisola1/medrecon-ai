"""
Tests for the MedRecon API health endpoint.
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    """
    The health endpoint should confirm that the API is running.

    This is intentionally a small smoke test. As the application
    grows, each agent and API layer will receive focused tests.
    """

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "ok"