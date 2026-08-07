import json
from langchain_core.prompts import PromptTemplate
from app.models.intents import IntentDetectionResult, BusinessIntent

class IntentDetector:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate.from_template(
            "Identify the business intent for this query: '{query}'.\n"
            "Valid intents are: Revenue Summary, Pipeline Health, Deal Lookup, Board Search, Operational Metrics, Project Status, Forecast, Leadership Update, Trend Analysis, Comparison.\n"
            "Return JSON with 'intent', 'confidence', 'requires_clarification'.\n"
        )

    def detect(self, query: str) -> IntentDetectionResult:
        # In a real implementation we would call self.llm.invoke(self.prompt.format(query=query))
        # and parse the output. Here we provide a mock detection logic for the demonstration.
        query_lower = query.lower()
        if "revenue" in query_lower:
            intent = BusinessIntent.REVENUE_SUMMARY
        elif "pipeline" in query_lower:
            intent = BusinessIntent.PIPELINE_HEALTH
        elif "deal" in query_lower:
            intent = BusinessIntent.DEAL_LOOKUP
        else:
            intent = BusinessIntent.OPERATIONAL_METRICS
            
        return IntentDetectionResult(
            intent=intent,
            confidence=0.9,
            requires_clarification=len(query.split()) < 2
        )
