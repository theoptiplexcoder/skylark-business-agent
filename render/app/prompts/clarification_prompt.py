from langchain_core.prompts import PromptTemplate

CLARIFICATION_PROMPT_TEMPLATE = """You are a Clarification Agent.
The user has submitted an ambiguous query.

User Query: "{query}"
Detected Entities: {entities}
Ambiguity Reason: {reason}

Formulate a polite, concise question asking the user to clarify their intent. Do not guess what they mean.

Clarification Question:
"""

CLARIFICATION_PROMPT = PromptTemplate(
    template=CLARIFICATION_PROMPT_TEMPLATE,
    input_variables=["query", "entities", "reason"]
)
