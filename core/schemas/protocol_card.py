from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any

class CandidateProtocol(BaseModel):
    title: str
    steps: list[str]
    rationale: str
    risk_notes: str | None = None

class ProtocolCard(BaseModel):
    case_id: str
    stage: str | None = None
    resilience_index: float = 0.5
    expected_life_expectancy_delta: float | None = None
    candidate_protocols: list[CandidateProtocol] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    reproducibility: dict[str, Any] = Field(default_factory=dict)
