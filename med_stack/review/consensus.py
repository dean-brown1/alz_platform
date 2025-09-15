"""
Consensus Synthesizer
---------------------
Combines board opinions while *excluding* boards that had no evidence.
This keeps "no-evidence" AIs from diluting or drowning out signals.
"""

from __future__ import annotations
from typing import Dict, Any, List


def compute_consensus(board_outputs: Dict[str, Dict[str, Any]], evidence_map: Dict[str, bool]) -> Dict[str, Any]:
    """
    Parameters
    ----------
    board_outputs: dict
        {board_name: {"opinion": {...}, "resilience": float|None, "protocols": [..], "had_evidence": bool}}
        "had_evidence" wins over evidence_map when provided.
    evidence_map: dict of modality->bool from the decomposer.

    Returns
    -------
    protocol_card: dict
        Minimal, reproducible synthesis with a continuous resilience_index and
        a list of deduplicated protocol steps.
    """
    considered: List[Dict[str, Any]] = []
    for board, out in (board_outputs or {}).items():
        if not isinstance(out, dict):
            continue
        had_evidence = out.get("had_evidence")
        # If a board explicitly declares evidence, trust it; otherwise infer from modalities
        if had_evidence is None:
            # Map a couple common board->modality inferences
            modality_guess = {
                "neurology": "clinical",
                "imaging": "imaging",
                "genomics": "genomics",
                "pharmaco": "pharma",
                "env": "environment",
            }.get(board, None)
            had_evidence = evidence_map.get(modality_guess, True) if modality_guess else True

        if not had_evidence:
            continue
        considered.append(out)

    if not considered:
        # Fallback: create a minimal baseline card
        return {
            "stage": None,
            "resilience_index": 0.5,
            "candidate_protocols": [{
                "title": "Baseline Cognitive Support",
                "steps": [
                    "Confirm diagnosis and stage",
                    "Assess lifestyle factors (sleep, activity, diet)",
                    "Consider cholinesterase inhibitor if appropriate",
                ],
                "rationale": "Heuristic baseline; no board had clear evidence.",
            }],
            "evidence": [],
            "limitations": ["Consensus fell back due to lack of evidence"],
        }

    # Aggregate resilience
    vals = [o.get("resilience") for o in considered if isinstance(o.get("resilience"), (int, float))]
    resilience = sum(vals) / len(vals) if vals else 0.5

    # Aggregate protocol suggestions (dedupe by step text)
    steps_seen = set()
    merged_steps: List[str] = []
    for o in considered:
        for p in o.get("protocols", []):
            if isinstance(p, str) and p.strip() and p not in steps_seen:
                steps_seen.add(p)
                merged_steps.append(p)

    return {
        "stage": None,
        "resilience_index": float(max(0.0, min(1.0, resilience))),
        "candidate_protocols": [{
            "title": "Board-merged plan",
            "steps": merged_steps or [
                "Confirm diagnosis and stage",
                "Assess lifestyle factors (sleep, activity, diet)",
            ],
            "rationale": "Merged across boards that had supporting evidence.",
        }],
        "evidence": [],
        "limitations": ["Preliminary; human review required"],
    }
