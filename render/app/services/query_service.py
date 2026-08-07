from app.core.logging import logger


class QueryService:
    """Query understanding and intent detection."""

    INTENTS = {
        "pipeline": ["pipeline", "funnel", "stages", "deals in progress"],
        "revenue": ["revenue", "income", "sales", "earnings", "money", "financial"],
        "sector": ["sector", "industry", "segment", "category", "vertical"],
        "operations": ["work order", "operations", "delivery", "completion", "project"],
        "forecast": ["forecast", "predict", "future", "outlook", "projection"],
        "leadership": ["leadership", "executive", "summary", "report", "update"],
        "risks": ["risk", "warning", "danger", "concern", "issue", "problem"],
        "comparison": ["compare", "versus", "vs", "against", "difference"],
    }

    TIME_KEYWORDS = {
        "today": "today",
        "yesterday": "yesterday",
        "this week": "this_week",
        "this month": "this_month",
        "this quarter": "this_quarter",
        "this year": "this_year",
        "last week": "last_week",
        "last month": "last_month",
        "last quarter": "last_quarter",
        "last year": "last_year",
    }

    def analyze_query(self, message: str) -> dict:
        message_lower = message.lower()

        intents = []
        for intent, keywords in self.INTENTS.items():
            if any(kw in message_lower for kw in keywords):
                intents.append(intent)

        time_period = None
        for keyword, period in self.TIME_KEYWORDS.items():
            if keyword in message_lower:
                time_period = period
                break

        needs_clarification = False
        clarification_question = None

        if not intents:
            needs_clarification = True
            clarification_question = "Could you clarify what business area you'd like to analyze? For example: pipeline, revenue, sector performance, or operations?"

        return {
            "intents": intents,
            "time_period": time_period or "all",
            "needs_clarification": needs_clarification,
            "clarification_question": clarification_question,
            "original_message": message,
        }

    def determine_required_boards(self, intents: list[str], available_boards: list[dict]) -> list[str]:
        board_names = {b.get("name", "").lower(): b.get("id") for b in available_boards}

        required = []
        for name, board_id in board_names.items():
            if any(kw in name for kw in ["deal", "sales", "pipeline", "revenue"]):
                required.append(board_id)
            elif any(kw in name for kw in ["work", "order", "project", "task", "operation"]):
                required.append(board_id)

        if not required and board_names:
            required = list(board_names.values())

        return required
