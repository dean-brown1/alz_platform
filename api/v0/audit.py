from fastapi import APIRouter, Query
from typing import Optional, List, Dict
from core.provenance.audit_sink import tail as file_tail
import datetime

router = APIRouter()

@router.get("/audit/tail")
def audit_tail(limit: int = Query(100, ge=1, le=1000), since: Optional[str] = None) -> List[Dict]:
    events = file_tail(limit=5000)  # read a generous slice
    if since:
        try:
            ts = datetime.datetime.fromisoformat(since.replace("Z", "+00:00")).isoformat().replace("+00:00", "Z")
            events = [e for e in events if e.get("ts") and e["ts"] >= ts]
        except Exception:
            # if not a timestamp, treat "since" as a request_id
            events = [e for e in events if e.get("request_id") == since]
    return events[-limit:]
# --- quick test endpoint to generate one audit event ---
from core.bus.events import emit_event

@router.post("/audit/test")
def audit_test():
    emit_event(who="diagnostic", action="ping", subject="audit")
    return {"ok": True}
