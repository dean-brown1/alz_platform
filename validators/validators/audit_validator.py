from validators.base import BaseValidator, ValidationResult
from core.schemas.case_bundle import CaseBundle
class AuditCompletenessValidator:
    code = "AUDIT_COMPLETE"
    description = "Sources have checksums; modalities declared"
    def run(self, case: CaseBundle):
        msgs = []
        for s in case.sources:
            if not s.checksum:
                msgs.append(f"Source {s.uri} missing checksum")
        if not case.modalities:
            msgs.append("No modalities set")
        if msgs:
            return [ValidationResult(code=self.code, severity="WARN", message="; ".join(msgs))]
        return []
def get_validator() -> BaseValidator:
    return AuditCompletenessValidator()
