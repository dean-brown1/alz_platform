import re
from validators.base import BaseValidator, ValidationResult
from core.schemas.case_bundle import CaseBundle
PII_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "US SSN-like"),
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "Email"),
    (r"\b\+?1?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "Phone"),
]
class PHIValidator:
    code = "PHI_SCAN"
    description = "PHI/PII scan of text observations"
    def run(self, case: CaseBundle):
        hits = []
        for obs in case.observations:
            for key, val in (obs.content or {}).items():
                if isinstance(val, str):
                    for pat, label in PII_PATTERNS:
                        if re.search(pat, val):
                            hits.append({"observation": obs.id, "field": key, "pattern": label})
        if hits:
            return [ValidationResult(code=self.code, severity="WARN", message=f"Potential PHI/PII: {len(hits)}", evidence={"hits": hits})]
        return []
def get_validator() -> BaseValidator:
    return PHIValidator()
