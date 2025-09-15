# med_stack/review/synthesis.py
from __future__ import annotations
from typing import Any, Dict, List

def _safe_get(d: Dict[str, Any], *path, default=None):
    cur = d
    try:
        for p in path:
            cur = cur[p]
        return cur
    except Exception:
        return default

def _collect_modalities(boards: Dict[str, Any]) -> list[str]:
    # include only boards with non-empty findings
    mod_map = {
        "neurology": "clinical",
        "clinical": "clinical",
        "imaging": "imaging",
        "genomics": "omics",
        "pharma": "pharma",
        "env": "environment",
    }
    mods: list[str] = []
    for k, v in boards.items():
        findings = (v or {}).get("findings") or []
        if findings and mod_map.get(k) and mod_map[k] not in mods:
            mods.append(mod_map[k])
    return mods or ["clinical"]

def synthesize_protocol_card(cb, boards: Dict[str, Any]) -> Dict[str, Any]:
    """Merge board findings to produce a protocol card.
    This function is defensive and works even if boards are sparse.
    """
    # Base RI
    ri = 0.50

    # Clinical contribution (if present)
    cln = boards.get("neurology") or boards.get("clinical") or {}
    ri_component = float(_safe_get(cln, "metrics", "ri_component", default=0.0) or 0.0)
    ri = max(0.0, min(1.0, ri + ri_component - 0.10))  # dampen a bit to avoid runaway

    # Candidate protocols (toy, transparent mapping)
    protos: List[Dict[str, Any]] = []
    if _safe_get(cln, "findings", default=[]):
        protos.append({
            "title": "Clinical Follow‑Up & Baseline Support",
            "steps": [
                "Schedule neurocognitive evaluation (MoCA/MMSE baseline)",
                "Review sleep/activity/diet; ensure caregiver notes captured",
                "Medication review; consider cholinesterase inhibitor if appropriate"
            ],
            "rationale": "Triggered by clinical board signal (see findings)."
        })
    else:
        protos.append({
            "title": "Clinical Follow-Up & Baseline Support",
            "steps": [
                "Schedule neurocognitive evaluation (MoCA/MMSE baseline)",
                "Review sleep/activity/diet; ensure caregiver notes captured",
                "Medication review; consider cholinesterase inhibitor if appropriate"
            ],
            "rationale": "Triggered by clinical board signal (see findings)."
        })

    # Case id (defensive extraction)
    case_id = None
    try:
        case_id = getattr(cb, "case_id", None) or getattr(cb, "id", None)
        if not case_id and hasattr(cb, "case"):
            case_id = cb.case.get("case_id") or cb.case.get("id")
    except Exception:
        case_id = None

    card: Dict[str, Any] = {
        "case_id": case_id or "unknown",
        "stage": None,
        "resilience_index": round(ri, 2),
        "expected_life_expectancy_delta": None,
        "candidate_protocols": protos,
        "evidence": [],
        "limitations": ["Heuristic; boards not yet model-merged"],
        "reproducibility": {
            "modalities": _collect_modalities(boards),
            "artifacts": []  # You can append export/audit paths here if desired
        }
    }
    return card
