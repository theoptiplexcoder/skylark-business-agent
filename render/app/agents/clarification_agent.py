from app.prompts.clarification_prompt import CLARIFICATION_PROMPT
from app.models.entities import Entities

class ClarificationAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def needs_clarification(self, query: str, intent: str, entities: Entities) -> bool:
        if intent == "Pipeline Health" and not entities.sectors and not entities.time_period:
            return True
        return False
        
    def ask_clarification(self, query: str, entities: Entities, reason: str) -> str:
        # Mock LLM call
        return f"Could you please specify which pipeline you are referring to? (e.g., Energy sector, this quarter)"
