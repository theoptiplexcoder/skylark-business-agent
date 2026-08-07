from typing import Optional, List
from pydantic import BaseModel


class TimePeriod(BaseModel):
    raw_text: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class Entities(BaseModel):
    clients: List[str] = []
    sectors: List[str] = []
    deals: List[str] = []
    projects: List[str] = []
    owners: List[str] = []
    countries: List[str] = []
    statuses: List[str] = []
    priorities: List[str] = []
    time_period: Optional[TimePeriod] = None
    requested_metrics: List[str] = []
