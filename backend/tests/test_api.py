"""
Integration tests for FastAPI endpoints using TestClient.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AgentTrace API"
    assert data["version"] == "0.1.0"
    assert data["status"] == "online"


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "mongodb" in data


def test_traces_404_for_nonexistent_trace():
    response = client.get("/api/v1/traces/non_existent_id_999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_traces_graph_404_for_nonexistent_trace():
    response = client.get("/api/v1/traces/non_existent_id_999999/graph")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_traces_analytics_404_for_nonexistent_trace():
    response = client.get("/api/v1/traces/non_existent_id_999999/analytics")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
