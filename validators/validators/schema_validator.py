from validators.base import BaseValidator, ValidationResult
from core.schemas.case_bundle import CaseBundle
class SchemaValidator:
    code = "SCHEMA_VALID"
    description = "CaseBundle-schema sanity checks"
    def run(self, case: CaseBundle):
        results = []
        if not case.case_id or not case.subject_id:
            results.append(ValidationResult(code=self.code, severity="BLOCK", message="Missing case_id or subject_id"))
        if not case.modalities:
            results.append(ValidationResult(code=self.code, severity="WARN", message="No modalities specified"))
        return results
def get_validator() -> BaseValidator:
    return SchemaValidator()
