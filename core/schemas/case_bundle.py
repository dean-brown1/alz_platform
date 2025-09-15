from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Any

Modality = Literal["clinical", "imaging", "omics", "pharma", "environment"]

class SourceRef(BaseModel):
    uri: str
    checksum: str | None = None
    modality: Modality

class Observation(BaseModel):
    id: str
    modality: Modality
    content: dict[str, Any]
    confidence: float | None = None

class Conflict(BaseModel):
    who: str
    what: str
    why: str | None = None
    severity: Literal["BLOCK","WARN","INFO"] = "WARN"

class QAFlag(BaseModel):
    code: str
    message: str
    severity: Literal["BLOCK","WARN","INFO"] = "WARN"

class CaseBundle(BaseModel):
    case_id: str
    subject_id: str
    modalities: list[Modality]
    sources: list[SourceRef] = Field(default_factory=list)
    observations: list[Observation] = Field(default_factory=list)
    unresolved_conflicts: list[Conflict] = Field(default_factory=list)
    tags: list[dict] = Field(default_factory=list)
    provenance: dict = Field(default_factory=dict)
    qa_flags: list[QAFlag] = Field(default_factory=list)
