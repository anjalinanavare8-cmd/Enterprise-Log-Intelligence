
from pydantic import BaseModel, Field


class LogCreate(BaseModel):
    timestamp: str = Field(..., min_length=1)
    service: str = Field(..., min_length=1, max_length=100)
    level: str = Field(..., min_length=1, max_length=20)
    error_code: str | None = None
    message: str = Field(..., min_length=1)
    response_time: float | None = Field(default=None, ge=0)


class LogResponse(BaseModel):
    id: int
    timestamp: str
    service: str
    level: str
    error_code: str | None
    message: str
    response_time: float | None
