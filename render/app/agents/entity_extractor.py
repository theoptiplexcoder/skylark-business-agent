import json
from langchain_core.prompts import PromptTemplate
from app.models.entities import Entities, TimePeriod

METRIC_KEYWORDS = {
    "revenue": ["revenue", "income", "sales", "earnings", "money", "total"],
    "amount": ["amount", "value", "deal value", "price", "cost"],
    "status": ["status", "stage", "phase", "state", "condition"],
    "date": ["date", "close date", "created", "updated", "deadline", "due", "timeline", "when"],
    "owner": ["owner", "assignee", "responsible", "manager", "lead", "who"],
    "sector": ["sector", "industry", "category", "segment", "vertical"],
    "priority": ["priority", "urgency", "importance", "level"],
    "client": ["client", "customer", "account", "company", "name"],
    "country": ["country", "region", "location", "area", "territory"],
    "description": ["description", "details", "notes", "summary", "info"],
    "progress": ["progress", "completion", "percent", "done", "finished"],
    "pipeline": ["pipeline", "funnel", "conversion", "win rate"],
    "forecast": ["forecast", "predicted", "expected", "projected", "outlook"],
    "margin": ["margin", "profit", "profitability", "markup"],
    "quantity": ["quantity", "count", "number", "units", "volume"],
    "tags": ["tags", "labels", "flags", "categories"],
}


class EntityExtractor:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate.from_template(
            "Extract business entities from the query: '{query}'.\n"
            "Return JSON with clients, sectors, deals, projects, owners, countries, statuses, priorities, time_period, and requested_metrics.\n"
        )

    def extract(self, query: str) -> Entities:
        query_lower = query.lower()
        requested_metrics = []
        for metric, keywords in METRIC_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                requested_metrics.append(metric)

        if not requested_metrics:
            requested_metrics = ["status", "date"]

        time_period = None
        time_patterns = {
            "today": "today",
            "yesterday": "yesterday",
            "this week": "this week",
            "this month": "this month",
            "this quarter": "this quarter",
            "this year": "this year",
            "last week": "last week",
            "last month": "last month",
            "last quarter": "last quarter",
            "last year": "last year",
        }
        for pattern, raw in time_patterns.items():
            if pattern in query_lower:
                time_period = TimePeriod(raw_text=raw)
                break

        sectors = []
        sector_keywords = ["energy", "tech", "finance", "healthcare", "manufacturing", "retail", "real estate"]
        for sector in sector_keywords:
            if sector in query_lower:
                sectors.append(sector.title())

        return Entities(
            sectors=sectors,
            time_period=time_period,
            requested_metrics=requested_metrics,
        )
