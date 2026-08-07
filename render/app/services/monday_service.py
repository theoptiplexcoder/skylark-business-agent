import httpx
import asyncio
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class MondayService:
    """Monday.com GraphQL API client."""

    def __init__(self):
        self.api_url = settings.MONDAY_API_URL
        self.api_key = settings.MONDAY_API_KEY
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "API-Version": "2024-10",
        }
        self.timeout = 30.0

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _execute_query(self, query: str, variables: Optional[dict] = None) -> dict:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                logger.error("Monday GraphQL errors: %s", data["errors"])
                raise Exception(f"Monday API errors: {data['errors']}")

            return data.get("data", {})

    async def check_health(self) -> bool:
        try:
            query = "{ me { id name email } }"
            result = await self._execute_query(query)
            return "me" in result
        except Exception as e:
            logger.error("Monday health check failed: %s", e)
            return False

    async def get_me(self) -> dict:
        query = "{ me { id name email account { name } } }"
        result = await self._execute_query(query)
        return result.get("me", {})

    async def get_boards(self) -> list[dict]:
        query = """
        query {
            boards(page: 1, per_page: 50) {
                id
                name
                description
                columns {
                    id
                    title
                    type
                    settings_str
                }
            }
        }
        """
        result = await self._execute_query(query)
        return result.get("boards", [])

    async def get_board(self, board_id: str) -> dict:
        query = """
        query ($boardId: [ID!]!) {
            boards(ids: $boardId) {
                id
                name
                description
                columns {
                    id
                    title
                    type
                    settings_str
                }
            }
        }
        """
        result = await self._execute_query(query, {"boardId": [board_id]})
        boards = result.get("boards", [])
        return boards[0] if boards else {}

    async def get_items(
        self, board_id: str, limit: int = 100, cursor: Optional[str] = None
    ) -> dict:
        query = """
        query ($boardId: [ID!]!, $limit: Int!, $cursor: String) {
            boards(ids: $boardId) {
                items_page(limit: $limit, cursor: $cursor) {
                    cursor
                    items {
                        id
                        name
                        column_values {
                            id
                            text
                            type
                            value
                        }
                        created_at
                        updated_at
                    }
                }
            }
        }
        """
        result = await self._execute_query(query, {
            "boardId": [board_id],
            "limit": limit,
            "cursor": cursor,
        })
        boards = result.get("boards", [])
        if boards:
            page = boards[0].get("items_page", {})
            return {
                "items": page.get("items", []),
                "cursor": page.get("cursor"),
            }
        return {"items": [], "cursor": None}

    async def get_all_items(self, board_id: str, max_items: int = 1000) -> list[dict]:
        all_items = []
        cursor = None

        while len(all_items) < max_items:
            batch_size = min(100, max_items - len(all_items))
            result = await self.get_items(board_id, limit=batch_size, cursor=cursor)
            items = result.get("items", [])
            all_items.extend(items)
            cursor = result.get("cursor")
            if not cursor or not items:
                break

        return all_items

    async def get_columns(self, board_id: str) -> list[dict]:
        query = """
        query ($boardId: [ID!]!) {
            boards(ids: $boardId) {
                columns {
                    id
                    title
                    type
                    settings_str
                }
            }
        }
        """
        result = await self._execute_query(query, {"boardId": [board_id]})
        boards = result.get("boards", [])
        if boards:
            return boards[0].get("columns", [])
        return []


monday_service = MondayService()
