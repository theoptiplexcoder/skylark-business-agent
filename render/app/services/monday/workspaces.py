"""Workspace and folder retrieval from Monday.com."""

from app.services.monday.client import get_client
from app.services.monday.cache import cached


async def get_workspaces() -> list[dict]:
    """Fetch all workspaces."""
    client = get_client()
    query = """
    query {
        workspaces {
            id
            name
            description
            kind
            created_at
            created_by { id name }
        }
    }
    """
    data = await client.execute(query)
    return [_normalize_workspace(w) for w in data.get("workspaces", [])]


async def get_workspace_by_id(workspace_id: str) -> dict:
    """Fetch a single workspace by ID."""
    client = get_client()
    query = """
    query ($id: [ID!]!) {
        workspaces(ids: $id) {
            id
            name
            description
            kind
            created_at
            created_by { id name }
        }
    }
    """
    data = await client.execute(query, {"id": [workspace_id]})
    workspaces = data.get("workspaces", [])
    return _normalize_workspace(workspaces[0]) if workspaces else {}


async def get_folders(workspace_id: str = None) -> list[dict]:
    """Fetch folders, optionally filtered by workspace."""
    client = get_client()

    if workspace_id:
        query = """
        query ($workspaceId: [ID!]!) {
            workspaces(ids: $workspaceId) {
                folders {
                    id
                    name
                    workspace_id
                }
            }
        }
        """
        data = await client.execute(query, {"workspaceId": [workspace_id]})
        workspaces = data.get("workspaces", [])
        if not workspaces:
            return []
        raw_folders = workspaces[0].get("folders", [])
    else:
        query = """
        query {
            workspaces {
                id
                folders {
                    id
                    name
                    workspace_id
                }
            }
        }
        """
        data = await client.execute(query)
        raw_folders = []
        for w in data.get("workspaces", []):
            raw_folders.extend(w.get("folders", []))

    return [{"id": str(f.get("id", "")), "name": f.get("name", ""), "workspace_id": str(f.get("workspace_id", ""))} for f in raw_folders]


async def get_connected_boards(board_id: str) -> list[dict]:
    """Fetch boards connected via two-way links or mirror columns."""
    client = get_client()
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
    data = await client.execute(query, {"boardId": [board_id]})
    boards = data.get("boards", [])
    if not boards:
        return []

    connected = []
    for col in boards[0].get("columns", []):
        if col.get("type") in ("board", "mirror"):
            import json
            settings = col.get("settings_str", "{}")
            if isinstance(settings, str):
                try:
                    settings = json.loads(settings)
                except (json.JSONDecodeError, TypeError):
                    settings = {}
            board_refs = settings.get("boardIds", settings.get("board_ids", []))
            for ref_id in board_refs:
                connected.append({
                    "column_id": col.get("id"),
                    "column_title": col.get("title"),
                    "column_type": col.get("type"),
                    "connected_board_id": str(ref_id),
                })

    return connected


def _normalize_workspace(raw: dict) -> dict:
    creator = raw.get("created_by", {}) or {}
    return {
        "id": str(raw.get("id", "")),
        "name": raw.get("name", ""),
        "description": raw.get("description", ""),
        "kind": raw.get("kind", ""),
        "created_at": raw.get("created_at", ""),
        "created_by": {
            "id": str(creator.get("id", "")),
            "name": creator.get("name", ""),
        },
    }
