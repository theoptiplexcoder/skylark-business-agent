"""Reusable GraphQL executor for Monday.com API."""

import time
import logging
from typing import Any, Optional

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from app.core.config import get_settings
from app.services.monday.exceptions import (
    MondayAuthError,
    MondayGraphQLError,
    MondayNetworkError,
    MondayNotFoundError,
    MondayPermissionError,
    MondayRateLimitError,
    MondayTimeoutError,
)

logger = logging.getLogger("skylark.monday.graphql")
settings = get_settings()

HTTP_STATUS_MAP = {
    401: MondayAuthError,
    403: MondayPermissionError,
    404: MondayNotFoundError,
    408: MondayTimeoutError,
    429: MondayRateLimitError,
    500: MondayNetworkError,
    502: MondayNetworkError,
    503: MondayNetworkError,
}


class GraphQLExecutor:
    """Executes GraphQL queries against the Monday.com API with retries and pagination."""

    def __init__(self, api_key: str, api_url: str = None, timeout: float = 30.0):
        self.api_url = api_url or settings.MONDAY_API_URL
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
            "API-Version": "2024-10",
        }
        self.timeout = timeout

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        retry=retry_if_exception_type((MondayRateLimitError, MondayNetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def execute(self, query: str, variables: dict = None) -> dict:
        """Execute a single GraphQL query."""
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        start = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url, json=payload, headers=self.headers
                )

                elapsed = time.monotonic() - start
                logger.info(
                    "Monday API call completed in %.2fs (status=%d)",
                    elapsed,
                    response.status_code,
                )

                if response.status_code in HTTP_STATUS_MAP:
                    exc_class = HTTP_STATUS_MAP[response.status_code]
                    if response.status_code == 429:
                        retry_after = float(response.headers.get("Retry-After", 60))
                        raise exc_class(retry_after=retry_after, query=query, variables=variables)
                    raise exc_class(
                        f"HTTP {response.status_code}: {response.text[:200]}",
                        query=query,
                        variables=variables,
                    )

                response.raise_for_status()
                data = response.json()

                if "errors" in data:
                    raise MondayGraphQLError(
                        errors=data["errors"], query=query, variables=variables
                    )

                return data.get("data", {})

        except httpx.TimeoutException as e:
            elapsed = time.monotonic() - start
            logger.error("Monday API timeout after %.2fs: %s", elapsed, e)
            raise MondayTimeoutError(
                f"Request timed out after {self.timeout}s",
                query=query,
                variables=variables,
            )
        except httpx.RequestError as e:
            elapsed = time.monotonic() - start
            logger.error("Monday API network error after %.2fs: %s", elapsed, e)
            raise MondayNetworkError(
                f"Network error: {str(e)}",
                query=query,
                variables=variables,
            )

    async def execute_paginated(
        self,
        query: str,
        variables: dict = None,
        page_size: int = 50,
        max_items: int = None,
    ) -> list[dict]:
        """Execute a paginated query, returning all items."""
        all_items: list[dict] = []
        cursor = None

        while True:
            current_vars = {**(variables or {}), "limit": page_size}
            if cursor:
                current_vars["cursor"] = cursor

            result = await self.execute(query, current_vars)

            items, next_cursor = self._extract_paginated(result, page_size)
            all_items.extend(items)

            logger.info(
                "Fetched %d items (total so far: %d)", len(items), len(all_items)
            )

            if max_items and len(all_items) >= max_items:
                all_items = all_items[:max_items]
                break

            if not next_cursor or not items:
                break

            cursor = next_cursor

        return all_items

    def _extract_paginated(self, data: dict, expected_limit: int) -> tuple[list[dict], Optional[str]]:
        """Extract items and next cursor from a paginated response."""
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                board = value[0]
                for page_key in ("items_page", "boards_page", "users_page"):
                    if page_key in board:
                        page = board[page_key]
                        items = page.get("items", page.get(page_key.replace("_page", ""), []))
                        next_cursor = page.get("cursor")
                        return items, next_cursor

                if "column_values" in board:
                    return [board], None

        for key, value in data.items():
            if isinstance(value, list):
                return value, None

        return [], None
