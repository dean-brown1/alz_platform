import structlog
from pathlib import Path
import json
from core.bus.events import emit_event

logger = structlog.get_logger()


def audit(who: str, action: str, subject: str | None = None, **details) -> None:
    """Emit an audit event and log it through structlog."""
    emit_event(who=who, action=action, subject=subject, **details)
    logger.info("audit", who=who, action=action, subject=subject, **details)


# -------------------------------------------------------------------
# Append-only audit for validation reports
# -------------------------------------------------------------------

_AUDIT_FILE = Path("logs/audit.ndjson")


def audit_append_ndjson(obj) -> None:
    """
    Append a single JSON object (or Pydantic model) as one line into logs/audit.ndjson.
    Creates directories/files if they do not exist.
    Works with Pydantic v1, v2, dicts, or plain dataclasses.
    """
    _AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Normalize object into JSON string
    line: str
    try:
        # Pydantic v2
        line = obj.model_dump_json()  # type: ignore[attr-defined]
    except Exception:
        try:
            # Pydantic v1
            line = obj.json()  # type: ignore[attr-defined]
        except Exception:
            try:
                # Already a dict or BaseModel
                if hasattr(obj, "dict"):
                    line = json.dumps(obj.dict())
                elif isinstance(obj, dict):
                    line = json.dumps(obj)
                else:
                    line = json.dumps(obj, default=lambda o: getattr(o, "__dict__", str(o)))
            except Exception as e:
                line = json.dumps({"error": f"Failed to serialize: {e}", "repr": repr(obj)})

    # Append as one line
    with _AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
