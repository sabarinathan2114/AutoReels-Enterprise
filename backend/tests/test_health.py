from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "AutoReels Enterprise"
    assert data["status"] == "online"
    assert "endpoints" in data

def test_health_liveness():
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "timestamp" in data
    assert "version" in data

def test_health_readiness():
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert data["storage"] == "writable"

def test_request_id_middleware():
    custom_id = "test-request-id-9999"
    response = client.get("/health/live", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_id

def test_plans_matrix():
    response = client.get("/api/plans")
    assert response.status_code == 200
    plans = response.json()
    assert len(plans) == 4
    tier_ids = [p["id"] for p in plans]
    assert "free" in tier_ids
    assert "plan_a" in tier_ids
    assert "plan_b" in tier_ids
    assert "plan_c" in tier_ids
