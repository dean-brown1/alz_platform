from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class Finding(BaseModel):
    # A normalized signal from a board. magnitude in [0,1].
    key: str
    magnitude: float = 0.0
    rationale: Optional[str] = None

class BoardResult(BaseModel):
    # Uniform result emitted by any board adapter.
    board: str
    findings: List[Finding] = Field(default_factory=list)
    # ri_component should be None if not computable with given inputs.
    ri_component: Optional[float] = None
    rationale: List[str] = Field(default_factory=list)
