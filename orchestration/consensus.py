from __future__ import annotations
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel, Field

DEFAULT_WEIGHTS = {
    "neurology": 0.40,
    "imaging": 0.20,
    "genomics": 0.15,
    "pharma": 0.15,
    "env": 0.10,
}

class Consensus(BaseModel):
    score: float = 0.0
    per_board: Dict[str, float] = Field(default_factory=dict)
    raw_scores: Dict[str, float] = Field(default_factory=dict)
    weights: Dict[str, float] = Field(default_factory=lambda: DEFAULT_WEIGHTS.copy())
    rationale: List[str] = Field(default_factory=list)

def compute(board_results: List[Any], weights: Dict[str, float] | None = None) -> Consensus:
    weights = weights or DEFAULT_WEIGHTS
    per_board: Dict[str, float] = {}
    raw_scores: Dict[str, float] = {}
    rationale: List[str] = []

    # Collect only boards that provided ri_component (non-None)
    contributing: List[Tuple[str, float]] = []
    for br in board_results:
        raw_scores[br.board] = br.ri_component if br.ri_component is not None else 0.0
        if br.ri_component is not None:
            contributing.append((br.board, float(br.ri_component)))
            per_board[br.board] = float(br.ri_component)
            rationale.append(f"{br.board}: ri_component={br.ri_component:.2f}")
        else:
            rationale.append(f"{br.board}: no-evidence -> excluded from weighted average")

    # Renormalize weights to the subset of contributing boards
    denom = sum(weights.get(b, 0.0) for b, _ in contributing)
    score = 0.0
    if denom > 0 and contributing:
        for b, s in contributing:
            w = weights.get(b, 0.0) / denom if denom > 0 else 0.0
            score += w * s
    else:
        # No contributing boards; score remains 0.0 but rationale clarifies why.
        rationale.append("No boards contributed ri_component; returning 0.0 by policy.")

    return Consensus(score=score, per_board=per_board, raw_scores=raw_scores, weights=weights, rationale=rationale)
