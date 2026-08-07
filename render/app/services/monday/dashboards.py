"""Dashboard retrieval from Monday.com."""

import json
from typing import Any, Optional

from app.services.monday.client import get_client
from app.services.monday.cache import cached
from app.services.monday.exceptions import MondayNotFoundError


async def get_dashboards() -> list[dict]:
    """Fetch all dashboards the current user has access to."""
    client = get_client()
    query = """
    query {
        dashboards {
            id
            name
            description
            owner_id
            created_at
            updated_at
            workspace_id
            board_ids
        }
    }
    """
    data = await client.execute(query)
    raw = data.get("dashboards", [])
    return [_normalize_dashboard(d) for d in raw]


@cached(ttl=300, prefix="dashboard")
async def get_dashboard_by_id(dashboard_id: str) -> dict:
    """Fetch a single dashboard by ID."""
    client = get_client()
    query = """
    query ($id: [ID!]!) {
        dashboards(ids: $id) {
            id
            name
            description
            owner_id
            created_at
            updated_at
            workspace_id
            board_ids
        }
    }
    """
    data = await client.execute(query, {"id": [dashboard_id]})
    dashboards = data.get("dashboards", [])
    if not dashboards:
        raise MondayNotFoundError(f"Dashboard {dashboard_id} not found")
    return _normalize_dashboard(dashboards[0])


async def get_dashboard_widgets(dashboard_id: str) -> list[dict]:
    """Fetch all widgets for a dashboard."""
    client = get_client()
    query = """
    query ($id: [ID!]!) {
        dashboards(ids: $id) {
            widgets {
                id
                name
                type
                config
                dashboard_id
            }
        }
    }
    """
    data = await client.execute(query, {"id": [dashboard_id]})
    dashboards = data.get("dashboards", [])
    if not dashboards:
        return []
    widgets = dashboards[0].get("widgets", [])
    return [_normalize_widget(w) for w in widgets]


async def get_dashboard_complete(dashboard_id: str) -> dict:
    """Fetch dashboard with all connected data: widgets, boards, items, metrics."""
    dashboard = await get_dashboard_by_id(dashboard_id)
    widgets = await get_dashboard_widgets(dashboard_id)

    board_ids = dashboard.get("board_ids", [])
    connected_boards = []

    for bid in board_ids:
        try:
            from app.services.monday.boards import get_board_by_id
            board = await get_board_by_id(str(bid))
            connected_boards.append(board)
        except Exception:
            connected_boards.append({"id": str(bid), "error": "Could not fetch board"})

    return {
        "dashboard": dashboard,
        "widgets": widgets,
        "connected_boards": connected_boards,
        "board_count": len(connected_boards),
        "widget_count": len(widgets),
    }


def _normalize_dashboard(raw: dict) -> dict:
    board_ids = raw.get("board_ids", "")
    if isinstance(board_ids, str) and board_ids:
        try:
            board_ids = json.loads(board_ids)
        except (json.JSONDecodeError, TypeError):
            board_ids = [b.strip() for b in board_ids.split(",") if b.strip()]
    elif not board_ids:
        board_ids = []

    return {
        "id": str(raw.get("id", "")),
        "name": raw.get("name", ""),
        "description": raw.get("description", ""),
        "owner_id": str(raw.get("owner_id", "")),
        "workspace_id": str(raw.get("workspace_id", "")) if raw.get("workspace_id") else None,
        "board_ids": board_ids,
        "created_at": raw.get("created_at", ""),
        "updated_at": raw.get("updated_at", ""),
    }


def _normalize_widget(raw: dict) -> dict:
    config = raw.get("config", "")
    if isinstance(config, str) and config:
        try:
            config = json.loads(config)
        except (json.JSONDecodeError, TypeError):
            pass

    return {
        "id": str(raw.get("id", "")),
        "name": raw.get("name", ""),
        "type": raw.get("type", ""),
        "config": config,
        "dashboard_id": str(raw.get("dashboard_id", "")),
    }
