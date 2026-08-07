from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)


class ChatResponse(BaseModel):
    answer: str
    charts: Optional[list[dict]] = None
    metrics: Optional[dict] = None
    insights: Optional[list[str]] = None
    recommendations: Optional[list[str]] = None
    warnings: Optional[list[str]] = None
    confidence: float = 0.0
    quality: Optional[dict] = None
    execution_time: Optional[float] = None
