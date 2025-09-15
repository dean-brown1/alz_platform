
# core/store/jobs_sqlite.py
from __future__ import annotations

import json, sqlite3
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, Optional

from config import DB_PATH

Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

_CONN = sqlite3.connect(DB_PATH, check_same_thread=False)
_CONN.row_factory = sqlite3.Row

def _init():
    _CONN.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
      id TEXT PRIMARY KEY,
      state TEXT,
      created_at TEXT,
      audit_ref TEXT,
      input_json TEXT,
      protocol_card_json TEXT,
      boards_json TEXT,
      validators_json TEXT,
      error TEXT
    )
    """)
    _CONN.commit()
_init()

def upsert_job(rec: Dict[str, Any]) -> None:
    _CONN.execute(
        """INSERT OR IGNORE INTO jobs
              (id, state, created_at, audit_ref, input_json)
              VALUES (?, ?, ?, ?, ?)""",
        (
            rec["id"],
            rec.get("state") or "queued",
            rec.get("created_at") or datetime.now(UTC).isoformat(),
            rec.get("audit_ref"),
            json.dumps(rec.get("input", {})),
        ),
    )
    update_job(
        rec["id"],
        state=rec.get("state"),
        audit_ref=rec.get("audit_ref"),
        protocol_card=rec.get("protocol_card"),
        boards=rec.get("boards"),
        validators=rec.get("validators"),
        error=rec.get("error"),
    )

def update_job(job_id: str, **kw: Any) -> None:
    cur = _CONN.execute("SELECT 1 FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not cur:
        _CONN.execute(
            "INSERT INTO jobs (id, state, created_at) VALUES (?, ?, ?)",
            (job_id, kw.get("state") or "queued", datetime.now(UTC).isoformat()),
        )
    sets, vals = [], []
    if "state" in kw and kw["state"] is not None:
        sets.append("state=?"); vals.append(kw["state"])
    if "audit_ref" in kw and kw["audit_ref"] is not None:
        sets.append("audit_ref=?"); vals.append(kw["audit_ref"])
    if "protocol_card" in kw and kw["protocol_card"] is not None:
        sets.append("protocol_card_json=?"); vals.append(json.dumps(kw["protocol_card"])) 
    if "boards" in kw and kw["boards"] is not None:
        sets.append("boards_json=?"); vals.append(json.dumps(kw["boards"])) 
    if "validators" in kw and kw["validators"] is not None:
        sets.append("validators_json=?"); vals.append(json.dumps(kw["validators"])) 
    if "error" in kw and kw["error"] is not None:
        sets.append("error=?"); vals.append(kw["error"]) 
    if sets:
        sql = f"UPDATE jobs SET {', '.join(sets)} WHERE id=?"
        vals.append(job_id)
        _CONN.execute(sql, tuple(vals))
        _CONN.commit()

def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    r = _CONN.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not r:
        return None
    def _load(col: str):
        v = r[col]
        return json.loads(v) if v else None
    return {
        "id": r["id"],
        "state": r["state"],
        "created_at": r["created_at"],
        "audit_ref": r["audit_ref"],
        "input": _load("input_json") or {},
        "protocol_card": _load("protocol_card_json"),
        "boards": _load("boards_json"),
        "validators": _load("validators_json") or [],
        "error": r["error"],
    }
