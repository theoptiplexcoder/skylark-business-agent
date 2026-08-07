"""Board, group, item, and column retrieval from Monday.com."""

from typing import Optional

from app.services.monday.client import get_client
from app.services.monday.cache import cached
from app.services.monday.exceptions import MondayNotFoundError


# ── Boards ─────────────────────────────────────────────────

async def get_boards() -> list[dict]:
    """Fetch all boards with columns."""
    client = get_client()
    query = """
    query {
        boards {
            id
            name
            description
            board_kind
            state
            workspace_id
            columns {
                id
                title
                type
                settings_str
            }
            groups {
                id
                title
                color
                position
            }
        }
    }
    """
    data = await client.execute(query)
    return [_normalize_board(b) for b in data.get("boards", [])]


@cached(ttl=300, prefix="board")
async def get_board_by_id(board_id: str) -> dict:
    """Fetch a single board by ID with full metadata."""
    client = get_client()
    query = """
    query ($id: [ID!]!) {
        boards(ids: $id) {
            id
            name
            description
            board_kind
            state
            workspace_id
            columns {
                id
                title
                type
                settings_str
            }
            groups {
                id
                title
                color
                position
            }
        }
    }
    """
    data = await client.execute(query, {"id": [board_id]})
    boards = data.get("boards", [])
    if not boards:
        raise MondayNotFoundError(f"Board {board_id} not found")
    return _normalize_board(boards[0])


# ── Groups ─────────────────────────────────────────────────

async def get_groups(board_id: str) -> list[dict]:
    """Fetch all groups for a board."""
    client = get_client()
    query = """
    query ($boardId: [ID!]!) {
        boards(ids: $boardId) {
            groups {
                id
                title
                color
                position
            }
        }
    }
    """
    data = await client.execute(query, {"boardId": [board_id]})
    boards = data.get("boards", [])
    if not boards:
        return []
    return [_normalize_group(g) for g in boards[0].get("groups", [])]


# ── Items ──────────────────────────────────────────────────

async def get_items(board_id: str, limit: int = 100, cursor: str = None, group_id: str = None) -> dict:
    """Fetch a page of items from a board."""
    client = get_client()
    query = """
    query ($boardId: [ID!]!, $limit: Int!, $cursor: String) {
        boards(ids: $boardId) {
            items_page(limit: $limit, cursor: $cursor) {
                cursor
                items {
                    id
                    name
                    group { id title }
                    column_values {
                        id
                        text
                        type
                        value
                    }
                    created_at
                    updated_at
                    creator { id name }
                }
            }
        }
    }
    """
    data = await client.execute(query, {"boardId": [board_id], "limit": limit, "cursor": cursor})
    boards = data.get("boards", [])
    if not boards:
        return {"items": [], "cursor": None}

    page = boards[0].get("items_page", {})
    items = [_normalize_item(i) for i in page.get("items", [])]

    if group_id:
        items = [i for i in items if i.get("group", {}).get("id") == group_id]

    return {"items": items, "cursor": page.get("cursor")}


async def get_all_items(board_id: str, max_items: int = 2000) -> list[dict]:
    """Fetch all items from a board with automatic pagination."""
    client = get_client()
    all_items = []
    cursor = None

    while len(all_items) < max_items:
        batch_size = min(100, max_items - len(all_items))
        result = await get_items(board_id, limit=batch_size, cursor=cursor)
        items = result.get("items", [])
        all_items.extend(items)
        cursor = result.get("cursor")
        if not cursor or not items:
            break

    return all_items


async def get_subitems(item_id: str) -> list[dict]:
    """Fetch subitems for an item."""
    client = get_client()
    query = """
    query ($itemId: [ID!]!) {
        items(ids: $itemId) {
            subitems {
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
    """
    data = await client.execute(query, {"itemId": [item_id]})
    items = data.get("items", [])
    if not items:
        return []
    return [_normalize_item(i) for i in items[0].get("subitems", [])]


# ── Columns ────────────────────────────────────────────────

async def get_columns(board_id: str) -> list[dict]:
    """Fetch all columns for a board."""
    client = get_client()
    query = """
    query ($boardId: [ID!]!) {
        boards(ids: $boardId) {
            columns {
                id
                title
                type
                settings_str
                width
            }
        }
    }
    """
    data = await client.execute(query, {"boardId": [board_id]})
    boards = data.get("boards", [])
    if not boards:
        return []
    return [_normalize_column(c) for c in boards[0].get("columns", [])]


async def get_column_value(board_id: str, item_id: str, column_id: str) -> dict:
    """Fetch a specific column value for an item."""
    client = get_client()
    query = """
    query ($boardId: [ID!]!, $itemId: [ID!]!) {
        boards(ids: $boardId) {
            items_page(limit: 1) {
                items {
                    id
                    column_values(ids: [$columnId]) {
                        id
                        text
                        type
                        value
                    }
                }
            }
        }
    }
    """
    data = await client.execute(query, {"boardId": [board_id], "itemId": [item_id], "columnId": column_id})
    boards = data.get("boards", [])
    if not boards:
        return {}
    items = boards[0].get("items_page", {}).get("items", [])
    if not items:
        return {}
    col_vals = items[0].get("column_values", [])
    return _normalize_column_value(col_vals[0]) if col_vals else {}


# ── Updates ────────────────────────────────────────────────

async def get_updates(item_id: str, limit: int = 50) -> list[dict]:
    """Fetch updates (comments) for an item."""
    client = get_client()
    query = """
    query ($itemId: [ID!]!, $limit: Int!) {
        items(ids: $itemId) {
            updates(limit: $limit) {
                id
                body
                created_at
                updated_at
                creator { id name }
            }
        }
    }
    """
    data = await client.execute(query, {"itemId": [item_id], "limit": limit})
    items = data.get("items", [])
    if not items:
        return []
    return [
        {
            "id": str(u.get("id", "")),
            "body": u.get("body", ""),
            "created_at": u.get("created_at", ""),
            "updated_at": u.get("updated_at", ""),
            "creator": {
                "id": str(u.get("creator", {}).get("id", "")),
                "name": u.get("creator", {}).get("name", ""),
            },
        }
        for u in items[0].get("updates", [])
    ]


async def get_recent_updates(board_id: str, limit: int = 20) -> list[dict]:
    """Fetch recent updates across all items in a board."""
    items_result = await get_items(board_id, limit=50)
    items = items_result.get("items", [])

    all_updates = []
    for item in items[:20]:
        updates = await get_updates(item["id"], limit=3)
        for u in updates:
            u["item_id"] = item["id"]
            u["item_name"] = item["name"]
            all_updates.append(u)

    all_updates.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return all_updates[:limit]


# ── Tags ───────────────────────────────────────────────────

async def get_tags() -> list[dict]:
    """Fetch all tags in the account."""
    client = get_client()
    query = """
    query {
        tags {
            id
            name
        }
    }
    """
    data = await client.execute(query)
    return [{"id": str(t.get("id", "")), "name": t.get("name", "")} for t in data.get("tags", [])]


# ── Normalizers ────────────────────────────────────────────

def _normalize_board(raw: dict) -> dict:
    return {
        "id": str(raw.get("id", "")),
        "name": raw.get("name", ""),
        "description": raw.get("description", ""),
        "board_kind": raw.get("board_kind", ""),
        "state": raw.get("state", ""),
        "workspace_id": str(raw.get("workspace_id", "")) if raw.get("workspace_id") else None,
        "columns": [_normalize_column(c) for c in raw.get("columns", [])],
        "groups": [_normalize_group(g) for g in raw.get("groups", [])],
    }


def _normalize_group(raw: dict) -> dict:
    return {
        "id": str(raw.get("id", "")),
        "title": raw.get("title", ""),
        "color": raw.get("color", ""),
        "position": raw.get("position", ""),
    }


def _normalize_item(raw: dict) -> dict:
    col_values = {}
    for cv in raw.get("column_values", []):
        col_values[cv.get("id", "")] = _normalize_column_value(cv)

    return {
        "id": str(raw.get("id", "")),
        "name": raw.get("name", ""),
        "group": {
            "id": str(raw.get("group", {}).get("id", "")),
            "title": raw.get("group", {}).get("title", ""),
        },
        "values": col_values,
        "created_at": raw.get("created_at", ""),
        "updated_at": raw.get("updated_at", ""),
        "creator": {
            "id": str(raw.get("creator", {}).get("id", "")),
            "name": raw.get("creator", {}).get("name", ""),
        },
    }


def _normalize_column_value(raw: dict) -> dict:
    value = raw.get("value", "")
    if isinstance(value, str) and value:
        try:
            import json
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            pass

    return {
        "id": raw.get("id", ""),
        "text": raw.get("text", ""),
        "type": raw.get("type", ""),
        "value": value,
    }


def _normalize_column(raw: dict) -> dict:
    settings = raw.get("settings_str", "")
    if isinstance(settings, str) and settings:
        try:
            import json
            settings = json.loads(settings)
        except (json.JSONDecodeError, TypeError):
            pass

    return {
        "id": raw.get("id", ""),
        "title": raw.get("title", ""),
        "type": raw.get("type", ""),
        "settings": settings,
        "width": raw.get("width", None),
    }
