from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Literal, Any
from core.schemas.case_bundle import CaseBundle
Severity = Literal["BLOCK","WARN","INFO"]
@dataclass
class ValidationResult:
    code: str
    severity: Severity
    message: str
    evidence: dict[str, Any] | None = None
    patch: dict[str, Any] | None = None
class BaseValidator(Protocol):
    code: str
    description: str
    def run(self, case: CaseBundle) -> list[ValidationResult]: ...
