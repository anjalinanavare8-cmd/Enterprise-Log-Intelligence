
from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    incident_code: str = Field(..., min_length=1)
    service: str = Field(..., min_length=1)
    severity: str = Field(..., min_length=1)
    detection_method: str = Field(default="Rule-based")
    reasons: list[str] = Field(default_factory=list)


class IncidentStatusUpdate(BaseModel):
    status: str = Field(..., min_length=1)
    note: str | None = None
