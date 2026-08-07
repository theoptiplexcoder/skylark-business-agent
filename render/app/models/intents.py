from enum import Enum
from pydantic import BaseModel


class BusinessIntent(str, Enum):
    REVENUE_SUMMARY = "Revenue Summary"
    PIPELINE_HEALTH = "Pipeline Health"
    DEAL_LOOKUP = "Deal Lookup"
    BOARD_SEARCH = "Board Search"
    OPERATIONAL_METRICS = "Operational Metrics"
    PROJECT_STATUS = "Project Status"
    FORECAST = "Forecast"
    LEADERSHIP_UPDATE = "Leadership Update"
    TREND_ANALYSIS = "Trend Analysis"
    COMPARISON = "Comparison"


class IntentDetectionResult(BaseModel):
    intent: BusinessIntent
    confidence: float
    requires_clarification: bool
