from __future__ import annotations
from typing import List
from boards.model import BoardResult

def validate_contract(results: List[BoardResult]) -> List[str]:
    issues = []
    for r in results:
        if r.ri_component is not None and not (0.0 <= r.ri_component <= 1.0):
            issues.append(f"{r.board}: ri_component out of range [0,1]: {r.ri_component}")
    return issues
