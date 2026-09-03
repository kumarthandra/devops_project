import sys
import os

sys.path.insert(0, os.path.abspath("backend"))

from app import app


def test_health():
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"
    assert data["service"] == "claims-backend"
    assert data["version"] == "9.9.9"