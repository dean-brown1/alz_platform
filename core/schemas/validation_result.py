from __future__ import annotations
from typing import Literal, Any, List, Optional, Dict
from pydantic import BaseModel

# -------------------------------------------------------------------
# Legacy validation result (what your existing validators return)
# -------------------------------------------------------------------

ResultSeverity = Literal["BLOCK", "WARN", "INFO"]

class ValidationResult(BaseModel):
    code: str
    severity: ResultSeverity
    message: str
    evidence: dict[str, Any] | None = None
    patch: dict[str, Any] | None = None


# -------------------------------------------------------------------
# Step 1: Transparent validator outcomes (new schema)
# -------------------------------------------------------------------

Decision = Literal["allow", "warn", "drop", "block"]
OutcomeSeverity = Literal["info", "low", "medium", "high", "critical"]

class Reason(BaseModel):
    code: str
    message: str
    data_path: Optional[str] = None
    rule_id: Optional[str] = None
    evidence_refs: Optional[List[str]] = None

class SourceRef(BaseModel):
    component: str        # e.g., "validators/validators/schema_validator.py"
    version: str          # e.g., "v0.2.1"
    line_hint: Optional[int] = None

class ValidatorOutcome(BaseModel):
    validator_name: str
    decision: Decision
    severity: OutcomeSeverity
    reasons: List[Reason]
    source: SourceRef
    duration_ms: Optional[int] = None
    metadata: Optional[Dict[str, str]] = None

class ValidationReport(BaseModel):
    job_id: str
    case_id: str
    started_at: str
    finished_at: str
    outcomes: List[ValidatorOutcome]
    overall: Decision
    engine_version: str  # e.g., "validators@0.3.0"
