from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional

class Demographics(BaseModel):
    age: Optional[float] = Field(None, description="Age in years")
    sex: Optional[str] = Field(None, description="Encoded sex; e.g., '1'=male, '2'=female, or string")
    handedness: Optional[str] = None

class JobRequest(BaseModel):
    demographics: Demographics = Field(default_factory=Demographics)
