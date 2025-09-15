from __future__ import annotations

import csv
import io
import os
import json as _json
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse

# Try persistent store first; fall back to in-memory
try:
    from core.store.jobs import get_job  # type: ignore
except Exception:  # pragma: no cover
    get_job = None  # type: ignore

try:
    # local accessor exposed by api/v0/jobs.py for fallback
    from api.v0.jobs import _get_job_local  # type: ignore
except Exception:  # pragma: no cover
    def _get_job_local(_id: str):  # type: ignore
        return None

router = APIRouter()

def _load_job(job_id: str) -> Dict[str, Any]:
    job = None
    if get_job:
        try:
            job = get_job(job_id)
        except Exception:
            job = None
    if not job:
        job = _get_job_local(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    # Normalize JobRecord → dict for consistent access
    if hasattr(job, "as_dict"):
        job = job.as_dict()
    return job

def _maybe_parse_json(v):
    if isinstance(v, str):
        try:
            return _json.loads(v)
        except Exception:
            return v
    return v

@router.get("/exports/protocol_card")
def export_protocol_card(id: str, fmt: str = "json"):
    job = _load_job(id)

    card = job.get("protocol_card") or job.get("consensus")
    # Normalize JSON-encoded card (store persists JSON as strings)
    if isinstance(card, str):
        try:
            card = _json.loads(card)
        except Exception:
            raise HTTPException(status_code=500, detail="protocol card malformed")

    if not isinstance(card, dict):
        raise HTTPException(status_code=404, detail="protocol card not available")

    if fmt == "json":
        return JSONResponse(card)

    if fmt == "csv":
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(["title", "steps", "rationale", "risk_notes"])
        for cp in card.get("candidate_protocols", []):
            steps_joined = " | ".join(map(str, cp.get("steps", [])))  # robust to non-str
            writer.writerow([
                cp.get("title", ""),
                steps_joined,
                cp.get("rationale", ""),
                cp.get("risk_notes", ""),
            ])
        return PlainTextResponse(output.getvalue(), media_type="text/csv")

    raise HTTPException(status_code=400, detail="unsupported format")

@router.get("/exports/job")
def export_job(id: str):
    job = _load_job(id)
    bundle = {
        "id": id,
        "state": job.get("state"),
        "audit_ref": os.path.join("logs", "audit.ndjson"),
        # Present parsed dicts if the store had JSON strings
        "protocol_card": _maybe_parse_json(job.get("protocol_card")) or _maybe_parse_json(job.get("consensus")),
        "boards": _maybe_parse_json(job.get("boards")) or {},
    }
    return JSONResponse(bundle)
