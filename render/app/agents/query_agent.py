import operator
import math
from typing import TypedDict, Annotated, Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

from app.models.query_plan import QueryPlan, FinalResponse, QualityReport
from app.models.entities import Entities
from app.models.intents import IntentDetectionResult, BusinessIntent

from app.agents.intent_detector import IntentDetector
from app.agents.entity_extractor import EntityExtractor
from app.agents.clarification_agent import ClarificationAgent
from app.agents.planner import PlannerAgent
from app.agents.query_builder import QueryBuilder
from app.services.monday.boards import get_boards as fetch_boards, get_all_items as fetch_all_items
from app.services.monday.client import get_client
from app.services.schema_service import schema_service
from app.services.metadata_service import metadata_service
from app.services.cleaning_service import cleaning_service


def sanitize(obj):
    """Recursively replace NaN/Inf with None for JSON serialization."""
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize(v) for v in obj]
    return obj

# Define State
class AgentState(TypedDict):
    query: str
    intent_result: IntentDetectionResult
    entities: Entities
    clarification_needed: bool
    clarification_question: str
    available_boards: List[Dict[str, Any]]
    query_plan: QueryPlan
    graphql_query: str
    raw_data: List[Dict[str, Any]]
    cleaned_data: List[Dict[str, Any]]
    quality_report: QualityReport

class QueryAgentWorkflow:
    def __init__(self, llm):
        self.llm = llm
        self.intent_detector = IntentDetector(llm)
        self.entity_extractor = EntityExtractor(llm)
        self.clarification_agent = ClarificationAgent(llm)
        self.planner = PlannerAgent(llm)
        self.query_builder = QueryBuilder(llm)
        
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Add Nodes
        workflow.add_node("fetch_boards", self.fetch_boards_node)
        workflow.add_node("detect_intent", self.detect_intent_node)
        workflow.add_node("extract_entities", self.extract_entities_node)
        workflow.add_node("check_clarification", self.check_clarification_node)
        workflow.add_node("plan_query", self.plan_query_node)
        workflow.add_node("build_graphql", self.build_graphql_node)
        workflow.add_node("fetch_data", self.fetch_data_node)
        workflow.add_node("clean_data", self.clean_data_node)
        
        # Add Edges
        workflow.set_entry_point("fetch_boards")
        workflow.add_edge("fetch_boards", "detect_intent")
        workflow.add_edge("detect_intent", "extract_entities")
        workflow.add_edge("extract_entities", "check_clarification")
        
        # Conditional Edge
        workflow.add_conditional_edges(
            "check_clarification",
            lambda x: "clarify" if x.get("clarification_needed") else "plan",
            {
                "clarify": END,
                "plan": "plan_query"
            }
        )
        
        workflow.add_edge("plan_query", "build_graphql")
        workflow.add_edge("build_graphql", "fetch_data")
        workflow.add_edge("fetch_data", "clean_data")
        workflow.add_edge("clean_data", END)
        
        return workflow.compile()

    # Node Implementations
    async def fetch_boards_node(self, state: AgentState):
        try:
            boards = await fetch_boards()
        except Exception:
            boards = []
        return {"available_boards": boards}

    async def detect_intent_node(self, state: AgentState):
        result = self.intent_detector.detect(state["query"])
        return {"intent_result": result}
        
    async def extract_entities_node(self, state: AgentState):
        entities = self.entity_extractor.extract(state["query"])
        return {"entities": entities}

    async def check_clarification_node(self, state: AgentState):
        needs_clarif = self.clarification_agent.needs_clarification(
            state["query"], 
            state["intent_result"].intent.value, 
            state["entities"]
        )
        if needs_clarif:
            question = self.clarification_agent.ask_clarification(state["query"], state["entities"], "Missing context")
            return {"clarification_needed": True, "clarification_question": question}
        return {"clarification_needed": False}
        
    async def plan_query_node(self, state: AgentState):
        plan = self.planner.create_plan(
            state["query"], 
            state["intent_result"].intent.value,
            state["entities"].model_dump(),
            available_boards=state.get("available_boards", [])
        )
        return {"query_plan": plan}

    async def build_graphql_node(self, state: AgentState):
        return {"graphql_query": ""}

    async def fetch_data_node(self, state: AgentState):
        boards = state["query_plan"].boards
        raw_items = []
        for board_id in boards:
            try:
                items = await fetch_all_items(board_id, max_items=500)
                raw_items.extend(items)
            except Exception:
                continue
        return {"raw_data": raw_items}

    async def clean_data_node(self, state: AgentState):
        raw_data = state.get("raw_data", [])
        available_boards = state.get("available_boards", [])
        column_map = {}
        for board in available_boards:
            for col in board.get("columns", []):
                column_map[col.get("id", "")] = col.get("title", col.get("id", ""))

        if raw_data:
            import pandas as pd
            import math
            rows = []
            for item in raw_data:
                row = {"id": item.get("id"), "name": item.get("name")}
                for col_id, col_val in item.get("values", {}).items():
                    text = col_val.get("text", "") if isinstance(col_val, dict) else col_val
                    row[col_id] = text
                    if col_id in column_map:
                        row[column_map[col_id]] = text
                rows.append(row)
            df = pd.DataFrame(rows)
            df, quality_dict = cleaning_service.clean_dataframe(df)
            df = df.where(pd.notnull(df), None)
            cleaned = []
            for record in df.to_dict(orient="records"):
                clean_record = {}
                for k, v in record.items():
                    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                        clean_record[k] = None
                    else:
                        clean_record[k] = v
                cleaned.append(clean_record)
        else:
            cleaned = []
            quality_dict = {"original_rows": 0, "cleaned_rows": 0, "duplicates_removed": 0, "missing_values": 0, "warnings": []}
        from app.models.query_plan import QualityReport
        quality = QualityReport(**quality_dict)
        return {"cleaned_data": cleaned, "quality_report": quality}

    async def run(self, query: str) -> FinalResponse | Dict[str, str]:
        initial_state = {"query": query}
        result = await self.graph.ainvoke(initial_state)
        
        if result.get("clarification_needed"):
            return {"clarification_question": result["clarification_question"]}
            
        response = FinalResponse(
            query_plan=result["query_plan"],
            data=result["cleaned_data"],
            quality=result["quality_report"]
        )
        return sanitize(response.model_dump())
