# tests/test_roundtrip_protocol_card.py
import time
from typing import Dict, Any
from fastapi.testclient import TestClient

from api.app import app  # uses your real app

client = TestClient(app)


def _post_job(payload: Dict[str, Any]) -> str:
    r = client.post("/v0/jobs", json=payload)
    assert r.status_code == 200, r.text
    jid = r.json()["job_id"]
    assert isinstance(jid, str) and jid
    return jid


def _wait_done(job_id: str, timeout_s: int = 20) -> Dict[str, Any]:
    """
    Poll until the job exists AND reaches a terminal state.
    Tolerates transient 404s from GET /v0/jobs/{id} while the job record is being created.
    """
    t0 = time.time()
    last_text = ""
    while True:
        r = client.get(f"/v0/jobs/{job_id}")
        if r.status_code == 200:
            j = r.json()
            if j.get("state") in ("done", "blocked", "error"):
                return j
            last_text = r.text
        elif r.status_code not in (200, 404):
            raise AssertionError(f"unexpected status {r.status_code}: {r.text}")
        if time.time() - t0 > timeout_s:
            raise AssertionError(
                f"job {job_id} did not finish in {timeout_s}s; "
                f"last={r.status_code} {last_text[:200]}"
            )
        time.sleep(0.2)


def test_jobs_roundtrip_protocol_card_json_and_csv():
    # Use 'notes' to ensure Neurology fires (no app changes required).
    job_id = _post_job({"notes": "memory decline and sleep fragmentation; please assess."})
    j = _wait_done(job_id)

    # JSON export
    r_json = client.get(f"/v0/exports/protocol_card?id={job_id}")
    assert r_json.status_code == 200, r_json.text
    pc = r_json.json()
    assert "candidate_protocols" in pc and isinstance(pc["candidate_protocols"], list)
    assert any("title" in p and "steps" in p for p in pc["candidate_protocols"])

    # CSV export
    r_csv = client.get(f"/v0/exports/protocol_card?id={job_id}&fmt=csv")
    assert r_csv.status_code == 200, r_csv.text
    body = r_csv.text.strip().splitlines()
    assert body[0].startswith("title,steps,rationale,risk_notes")
    assert len(body) >= 2  # at least one protocol row

    # Audit pointer present on the job
    assert "audit_ref" in j and isinstance(j["audit_ref"], str) and j["audit_ref"].endswith("logs/audit.ndjson")
