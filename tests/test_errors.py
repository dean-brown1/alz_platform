from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_404_problem_json():
    r = client.get("/v0/does-not-exist")
    assert r.status_code == 404
    # Should be RFC 7807 style
    assert r.headers.get("content-type", "").startswith("application/problem+json")
    body = r.json()
    for key in ("type", "title", "status", "instance"):
        assert key in body
    assert body["status"] == 404
