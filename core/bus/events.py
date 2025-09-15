from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
from datetime import datetime, timezone

# append-only file sink + tail reader
from core.provenance.audit_sink import write_line as _write_line, tail

@dataclass
class AuditEvent:
    when: str
    who: str
    action: str
    subject: str | None = None
    details: dict[str, Any] | None = None

def emit_event(who: str, action: str, subject: str | None = None, **details: Any) -> None:
    event = AuditEvent(
        when=datetime.now(timezone.utc).isoformat(),
        who=who,
        action=action,
        subject=subject,
        details=details or None,
    )
    # write one JSON line to logs/audit.ndjson
    _write_line(asdict(event))

def get_events() -> list[dict]:
    # keep legacy API by reading recent lines from the file
    return tail(limit=1000)
