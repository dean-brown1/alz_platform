from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal

class DataTaterTag(BaseModel):
    tag_id: str
    concept_id: str
    modality: Literal["clinical","imaging","omics","pharma","environment"]
    value: str | float | int | None = None
    units: str | None = None
    span_or_region: dict | None = None
    confidence: float | None = None
    version: str = "1.0"
    evidence_pointer: str | None = None
