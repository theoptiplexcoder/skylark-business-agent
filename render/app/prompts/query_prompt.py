from langchain_core.prompts import PromptTemplate

QUERY_BUILDER_PROMPT_TEMPLATE = """You are a monday.com GraphQL Query Builder.
Given the target boards, columns, and filters, generate a valid GraphQL query.

Target Boards: {boards}
Required Columns: {columns}
Filters: {filters}
Board Metadata Context: {metadata}

IMPORTANT:
- Use the standard `boards(ids: [...]) {{ items_page(...) {{ items {{ column_values(...) {{ ... }} }} }} }}` structure if querying items.
- Only request the specific column IDs provided.

Generate ONLY the GraphQL query string.
"""

QUERY_PROMPT = PromptTemplate(
    template=QUERY_BUILDER_PROMPT_TEMPLATE,
    input_variables=["boards", "columns", "filters", "metadata"]
)
