from pydantic import BaseModel
from typing import Optional


class BoardResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    columns: Optional[list[dict]] = None


class MetricsResponse(BaseModel):
    pipeline_value: float = 0
    revenue: float = 0
    win_rate: float = 0
    active_deals: int = 0
    work_orders: int = 0
    completed_orders: int = 0
    avg_deal_size: float = 0
    completion_pct: float = 0


class LeadershipRequest(BaseModel):
    period: Optional[str] = "current"


class LeadershipResponse(BaseModel):
    summary: str = ""
    wins: list[str] = []
    risks: list[str] = []
    opportunities: list[str] = []
    recommendations: list[str] = []
