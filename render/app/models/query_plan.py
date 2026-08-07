from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class QueryPlan(BaseModel):
    intent: str
    boards: List[str] = []
    filters: Dict[str, Any] = {}
    columns: List[str] = []


class QualityReport(BaseModel):
    original_rows: int = 0
    cleaned_rows: int = 0
    duplicates_removed: int = 0
    missing_values: int = 0
    warnings: List[str] = []


class FinalResponse(BaseModel):
    query_plan: QueryPlan
    data: List[Dict[str, Any]] = []
    quality: QualityReport
