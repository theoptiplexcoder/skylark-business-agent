import json
from app.prompts.planner_prompt import PLANNER_PROMPT
from app.models.query_plan import QueryPlan

METRIC_TO_COLUMN_KEYWORDS = {
    "revenue": ["revenue", "income", "sales", "amount", "value", "deal value", "total", "price"],
    "amount": ["amount", "value", "deal value", "price", "cost", "total", "revenue"],
    "status": ["status", "stage", "phase", "state", "condition", "deal stage", "pipeline stage"],
    "date": ["date", "close date", "created", "updated", "deadline", "due", "timeline", "expected close"],
    "owner": ["owner", "assignee", "responsible", "manager", "lead", "person", "team"],
    "sector": ["sector", "industry", "category", "segment", "vertical", "market"],
    "priority": ["priority", "urgency", "importance", "level"],
    "client": ["client", "customer", "account", "company", "name", "contact"],
    "country": ["country", "region", "location", "area", "territory", "city"],
    "description": ["description", "details", "notes", "summary", "info", "title", "name"],
    "progress": ["progress", "completion", "percent", "done", "finished", "%"],
    "pipeline": ["pipeline", "funnel", "conversion", "win rate", "stage"],
    "forecast": ["forecast", "predicted", "expected", "projected", "outlook"],
    "margin": ["margin", "profit", "profitability", "markup", "cost"],
    "quantity": ["quantity", "count", "number", "units", "volume", "items"],
    "tags": ["tags", "labels", "flags", "categories", "group"],
}


class PlannerAgent:
    def __init__(self, llm):
        self.llm = llm

    def _match_columns(self, requested_metrics: list[str], available_boards: list[dict], matched_board_ids: list[str]) -> list[str]:
        matched_columns = []
        seen_column_ids = set()

        for board in available_boards:
            if str(board.get("id")) not in matched_board_ids:
                continue
            for col in board.get("columns", []):
                col_title = col.get("title", "").lower()
                col_id = col.get("id", "")
                if col_id in seen_column_ids:
                    continue
                for metric in requested_metrics:
                    keywords = METRIC_TO_COLUMN_KEYWORDS.get(metric, [])
                    if any(kw in col_title for kw in keywords):
                        matched_columns.append(col.get("title", col_id))
                        seen_column_ids.add(col_id)
                        break

        return matched_columns

    def create_plan(self, query: str, intent: str, entities: dict, available_boards: list[dict] = None) -> QueryPlan:
        query_lower = query.lower()
        matched_board_ids = []
        requested_metrics = entities.get("requested_metrics", ["status", "date"])

        if available_boards:
            for board in available_boards:
                board_name = board.get("name", "").lower()
                board_id = str(board.get("id", ""))

                if intent == "Revenue Summary" and any(kw in board_name for kw in ["deal", "sales", "pipeline", "revenue", "income"]):
                    matched_board_ids.append(board_id)
                elif intent == "Pipeline Health" and any(kw in board_name for kw in ["deal", "sales", "pipeline", "funnel"]):
                    matched_board_ids.append(board_id)
                elif intent == "Deal Lookup" and any(kw in board_name for kw in ["deal", "sales", "pipeline"]):
                    matched_board_ids.append(board_id)
                elif intent == "Operational Metrics" and any(kw in board_name for kw in ["work", "order", "project", "task", "operation"]):
                    matched_board_ids.append(board_id)
                elif intent == "Project Status" and any(kw in board_name for kw in ["project", "task", "work"]):
                    matched_board_ids.append(board_id)
                elif any(kw in board_name for kw in ["deal", "sales", "pipeline", "revenue"]):
                    matched_board_ids.append(board_id)
                elif any(kw in board_name for kw in ["work", "order", "project", "task"]):
                    matched_board_ids.append(board_id)

            if not matched_board_ids:
                matched_board_ids = [str(b.get("id", "")) for b in available_boards[:3]]

        matched_columns = self._match_columns(requested_metrics, available_boards or [], matched_board_ids)

        if not matched_columns:
            matched_columns = requested_metrics

        return QueryPlan(
            intent=intent,
            boards=matched_board_ids,
            filters=entities,
            columns=matched_columns
        )
