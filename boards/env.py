from __future__ import annotations
from typing import Dict, Any
from .model import BoardResult

def run(payload: Dict[str, Any]) -> BoardResult:
    # With demographics only, environment board has no signal.
    return BoardResult(board="env", findings=[], ri_component=None, rationale=["No environment inputs present."])
