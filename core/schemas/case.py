from __future__ import annotations
from pydantic import BaseModel, Field, model_validator
from typing import Any, Dict

class Case(BaseModel):
    case_id: str = Field(min_length=1, max_length=128)
    clinical_notes: str | None = Field(default=None, max_length=20000)
    imaging: Dict[str, Any] | None = None
    omics: Dict[str, Any] | None = None
    pharma: Dict[str, Any] | None = None
    environment: Dict[str, Any] | None = None

    @model_validator(mode="after")
    def _require_some_signal(self) -> "Case":
        if not any([self.clinical_notes, self.imaging, self.omics, self.pharma, self.environment]):
            raise ValueError(
                "At least one of clinical_notes, imaging, omics, pharma, environment is required"
            )
        return self
