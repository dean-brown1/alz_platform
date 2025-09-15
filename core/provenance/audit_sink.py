from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, timezone
import threading, json, hashlib

AUDIT_DIR = Path("logs")
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_FILE = AUDIT_DIR / "audit.ndjson"
_LOCK = threading.Lock()

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def sha256_json(obj: Any) -> str:
    # default=str ensures we can hash datetimes and other simple objects
    data = json.dumps(obj, separators=(",", ":"), sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()

def write_line(event: Dict[str, Any]) -> None:
    if "ts" not in event:
        event["ts"] = now_iso()
    line = json.dumps(event, separators=(",", ":"), ensure_ascii=False) + "\n"
    with _LOCK:
        with AUDIT_FILE.open("a", encoding="utf-8") as f:
            f.write(line)

def tail(limit: int = 1000) -> List[Dict[str, Any]]:
    if not AUDIT_FILE.exists():
        return []
    with AUDIT_FILE.open("r", encoding="utf-8") as f:
        lines = [ln for ln in f if ln.strip()]
    return [json.loads(ln) for ln in lines[-limit:]]
