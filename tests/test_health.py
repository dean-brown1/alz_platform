from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_live_ok():
    r = client.get("/v0/live")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

def test_ready_shape():
    r = client.get("/v0/ready")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ok"
    assert "checks" in body
