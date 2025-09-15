from __future__ import annotations
from typing import Dict, Any, List
from .model import BoardResult, Finding

def run(payload: Dict[str, Any]) -> BoardResult:
    dem = (payload or {}).get("demographics", {}) or {}
    sex = str(dem.get("sex")) if dem else None

    findings: List[Finding] = []
    rationale: List[str] = []

    # Example: extremely light prior—this is placeholder logic.
    # Replace with validated rules/ML in your pipeline.
    if sex in {"1", "male", "M", "m"}:
        findings.append(Finding(key="sex_male", magnitude=0.00, rationale="Sex alone is not determinative"))
    elif sex in {"2", "female", "F", "f"}:
        findings.append(Finding(key="sex_female", magnitude=0.00, rationale="Sex alone is not determinative"))

    # Neurology board chooses not to compute ri_component with demographics-only input.
    ri_component = None
    rationale.append("Demographics-only input: deferring ri_component; insufficient evidence.")

    return BoardResult(board="neurology", findings=findings, ri_component=ri_component, rationale=rationale)
