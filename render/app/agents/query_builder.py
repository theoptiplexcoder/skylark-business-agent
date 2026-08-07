import json
from app.prompts.query_prompt import QUERY_PROMPT

class QueryBuilder:
    def __init__(self, llm):
        self.llm = llm

    def build_graphql(self, boards: list[str], columns: list[str], filters: dict, metadata: list[dict]) -> str:
        # Generate basic GraphQL query based on the monday API structure
        board_ids = json.dumps(boards)
        # Assuming simple fetch of items based on column logic
        query = f"""
        query {{
            boards(ids: {board_ids}) {{
                items_page(limit: 50) {{
                    cursor
                    items {{
                        id
                        name
                        column_values {{
                            id
                            text
                            value
                        }}
                    }}
                }}
            }}
        }}
        """
        return query
