from __future__ import annotations

from typing import Any, Dict, List
from types import SimpleNamespace

# Corrected import per COMPAT-002
try:
    from core.decomposer import select_boards as plan  # type: ignore
except Exception:  # pragma: no cover
    plan = None  # type: ignore

try:
    from orchestration.consensus import compute as compute_consensus  # type: ignore
except Exception:  # pragma: no cover
    def compute_consensus(_):  # type: ignore
        return SimpleNamespace(model_dump=lambda: {"resilience_index": 0.0})

try:
    from med_stack.review.synthesis import synthesize_protocol_card  # type: ignore
except Exception:  # pragma: no cover
    def synthesize_protocol_card(cb, boards_map):  # type: ignore
        return {"case_id": getattr(cb, "case_id", None), "candidate_protocols": [], "evidence": []}

# BOARD_RUNNERS should be provided elsewhere in the codebase.
# We import lazily and degrade gracefully if absent.
try:
    from api.board_runners import BOARD_RUNNERS  # type: ignore
except Exception:  # pragma: no cover
    BOARD_RUNNERS = {}

def run_boards(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Select boards, run them, compute consensus, and return a protocol card."""
    # 1) Select targets via planner (no extra fallback here)
    targets: List[str] = []
    evidence = None
    try:
        if plan:
            targets, evidence = plan(payload)
    except Exception:
        targets = []

    # 2) Execute selected boards
    results = []
    for b in targets:
        fn = BOARD_RUNNERS.get(b)
        if not fn:
            continue
        try:
            results.append(fn(payload))
        except Exception:
            continue

    # 3) Normalize results (dict or pydantic) and build boards_map
    norm_results = []
    boards_map: Dict[str, Any] = {}
    for i, r in enumerate(results):
        if hasattr(r, "model_dump"):
            d = r.model_dump()
        elif isinstance(r, dict):
            d = r
        else:
            d = {"raw": r}
        key = d.get("board") or d.get("role") or f"board_{i}"
        norm_results.append(d)
        boards_map[key] = d

    # 4) Build consensus inputs as objects with attributes
    cons_inputs = []
    for d in norm_results:
        key = d.get("board") or d.get("role") or "unknown"
        metrics = d.get("metrics") or {}
        try:
            ri = float((metrics or {}).get("ri_component") or 0.0)
        except Exception:
            ri = 0.0
        cons_inputs.append(SimpleNamespace(board=key, ri_component=ri))

    consensus = compute_consensus(cons_inputs)

    # 5) Protocol Card
    cb = SimpleNamespace(case_id=payload.get("case_id"))
    protocol_card = synthesize_protocol_card(cb, boards_map)

    return {
        "boards": norm_results,
        "consensus": consensus.model_dump() if hasattr(consensus, "model_dump") else consensus,
        "protocol_card": protocol_card,
    }
