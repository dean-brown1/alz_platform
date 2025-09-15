from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, List, Dict
class RoleOutput(BaseModel):
    findings: Dict[str, Any] | List[Any] = Field(default_factory=list)
    notes: str | None = None
    evidence: Dict[str, Any] | None = None
