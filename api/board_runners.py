from __future__ import annotations
from typing import Any, Dict

from project_stack.pipelines import steps
from med_stack.board.roles import neurology_ai, imaging_ai, genomics_ai, pharmaco_ai, env_ai

def _to_casebundle(payload: Dict[str, Any]):
    """Build a CaseBundle once from raw input via the project pipeline."""
    cb = steps.ingest(payload)
    cb = steps.normalize(cb)
    return cb

def _adapt(name: str, out: Any) -> Dict[str, Any]:
    """
    Normalize various role outputs to the canonical board dict the rest
    of the system expects: {board, findings, notes, metrics}.
    - neurology_ai already returns this shape.
    - imaging/genomics/pharmaco/env return {"role": "...", "raw": RoleOutput}.
      We adapt them to the canonical form with ri_component=0.0 baseline.
    """
    if hasattr(out, "model_dump"):
        d = out.model_dump()
    elif isinstance(out, dict):
        d = out
    else:
        return {"board": name, "findings": [], "notes": "", "metrics": {"ri_component": 0.0}}

    # If it's already the canonical board dict (neurology/clinical), return as-is.
    if "board" in d and "findings" in d and "metrics" in d:
        return d

    raw = d.get("raw", d) if isinstance(d, dict) else {}
    findings = []
    notes = ""
    if isinstance(raw, dict):
        findings = raw.get("findings") or []
        notes = raw.get("notes") or ""

    return {
        "board": name,
        "findings": findings if isinstance(findings, list) else [],
        "notes": notes if isinstance(notes, str) else "",
        "metrics": {"ri_component": 0.0},  # RI contribution baseline for non-clinical boards
    }

# --- Individual runners (payload -> CaseBundle -> board.analyze -> adapted dict) ---

def run_neurology(payload: Dict[str, Any]) -> Dict[str, Any]:
    cb = _to_casebundle(payload)
    out = neurology_ai.analyze(cb)  # returns canonical dict already
    return _adapt("clinical", out)  # expose under 'clinical' key for synthesis

def run_imaging(payload: Dict[str, Any]) -> Dict[str, Any]:
    cb = _to_casebundle(payload)
    out = imaging_ai.analyze(cb)
    return _adapt("imaging", out)

def run_genomics(payload: Dict[str, Any]) -> Dict[str, Any]:
    cb = _to_casebundle(payload)
    out = genomics_ai.analyze(cb)
    return _adapt("genomics", out)

def run_pharmaco(payload: Dict[str, Any]) -> Dict[str, Any]:
    cb = _to_casebundle(payload)
    out = pharmaco_ai.analyze(cb)
    return _adapt("pharmaco", out)

def run_env(payload: Dict[str, Any]) -> Dict[str, Any]:
    cb = _to_casebundle(payload)
    out = env_ai.analyze(cb)
    return _adapt("environment", out)

# --- Registry consumed by api/hooks.run_boards (no stubs, all real boards wired) ---

BOARD_RUNNERS = {
    "neurology": run_neurology,   # maps to clinical board in synthesis
    "imaging": run_imaging,
    "genomics": run_genomics,
    "pharmaco": run_pharmaco,
    "env": run_env,
}
