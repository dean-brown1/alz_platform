"""
Decomposer / Router (patched minimal)
------------------------------------
- Detects modalities from loose keys
- Runs only boards with evidence
- If none found, falls back to ["neurology"] AND marks clinical=True so evidence reflects fallback
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple

MODALITY_KEYS = {
    "demographics": ["demographics", "patient", "age", "sex", "handedness"],
    "clinical": ["clinical", "notes", "symptoms", "mmse", "moca", "cdr"],
    "imaging": ["imaging", "mri", "pet", "ct", "fmri", "dti"],
    "genomics": ["genomics", "omics", "genotype", "snps", "wgs", "rna_seq"],
    "pharma": ["pharma", "meds", "medications", "drugs", "rx"],
    "environment": ["env", "environment", "exposure", "lifestyle", "sleep", "activity", "diet"],
}
MODALITY_TO_BOARD = {
    "clinical": "neurology",
    "imaging": "imaging",
    "genomics": "genomics",
    "pharma": "pharmaco",
    "environment": "env",
}
FALLBACK_BOARDS: List[str] = ["neurology"]

def _has_any_key(obj: Dict[str, Any], keys: List[str]) -> bool:
    if not isinstance(obj, dict):
        return False
    lower_keys = {str(k).lower() for k in obj.keys()}
    for k in keys:
        if k.lower() in lower_keys:
            return True
    for v in obj.values():
        if isinstance(v, dict):
            lv = {str(k).lower() for k in v.keys()}
            if any(k.lower() in lv for k in keys):
                return True
    return False

def detect_modalities(case: Dict[str, Any]) -> Dict[str, bool]:
    evidence = {}
    for modality, keys in MODALITY_KEYS.items():
        evidence[modality] = _has_any_key(case, keys)
    return evidence

def select_boards(case: Dict[str, Any]) -> Tuple[List[str], Dict[str, bool]]:
    ev = detect_modalities(case)
    boards: List[str] = []
    for modality, has in ev.items():
        if not has:
            continue
        board = MODALITY_TO_BOARD.get(modality)
        if board and board not in boards:
            boards.append(board)

    if not boards:
        boards = FALLBACK_BOARDS.copy()
        # Make the fallback explicit in evidence so downstream consensus doesn't think
        # "no clinical evidence" and can still reason about neurology baseline.
        ev["clinical"] = True

    return boards, ev
