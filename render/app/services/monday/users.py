"""User and team retrieval from Monday.com."""

from app.services.monday.client import get_client
from app.services.monday.cache import cached


async def get_users() -> list[dict]:
    """Fetch all users in the account."""
    client = get_client()
    query = """
    query {
        users {
            id
            name
            email
            title
            photo_url
            is_guest
            is_pending
            created_at
        }
    }
    """
    data = await client.execute(query)
    return [_normalize_user(u) for u in data.get("users", [])]


async def get_user_by_id(user_id: str) -> dict:
    """Fetch a single user by ID."""
    client = get_client()
    query = """
    query ($id: [ID!]!) {
        users(ids: $id) {
            id
            name
            email
            title
            photo_url
            is_guest
            is_pending
            created_at
        }
    }
    """
    data = await client.execute(query, {"id": [user_id]})
    users = data.get("users", [])
    return _normalize_user(users[0]) if users else {}


async def get_teams() -> list[dict]:
    """Fetch all teams."""
    client = get_client()
    query = """
    query {
        teams {
            id
            name
            description
            users {
                id
                name
            }
        }
    }
    """
    data = await client.execute(query)
    return [_normalize_team(t) for t in data.get("teams", [])]


async def get_team_by_id(team_id: str) -> dict:
    """Fetch a single team by ID."""
    client = get_client()
    query = """
    query ($id: [ID!]!) {
        teams(ids: $id) {
            id
            name
            description
            users {
                id
                name
            }
        }
    }
    """
    data = await client.execute(query, {"id": [team_id]})
    teams = data.get("teams", [])
    return _normalize_team(teams[0]) if teams else {}


async def get_board_subscribers(board_id: str) -> list[dict]:
    """Fetch people subscribed to a board."""
    client = get_client()
    query = """
    query ($boardId: [ID!]!) {
        boards(ids: $boardId) {
            subscribers {
                id
                name
                email
            }
        }
    }
    """
    data = await client.execute(query, {"boardId": [board_id]})
    boards = data.get("boards", [])
    if not boards:
        return []
    return [
        {"id": str(s.get("id", "")), "name": s.get("name", ""), "email": s.get("email", "")}
        for s in boards[0].get("subscribers", [])
    ]


def _normalize_user(raw: dict) -> dict:
    return {
        "id": str(raw.get("id", "")),
        "name": raw.get("name", ""),
        "email": raw.get("email", ""),
        "title": raw.get("title", ""),
        "photo_url": raw.get("photo_url", ""),
        "is_guest": raw.get("is_guest", False),
        "is_pending": raw.get("is_pending", False),
        "created_at": raw.get("created_at", ""),
    }


def _normalize_team(raw: dict) -> dict:
    return {
        "id": str(raw.get("id", "")),
        "name": raw.get("name", ""),
        "description": raw.get("description", ""),
        "members": [
            {"id": str(u.get("id", "")), "name": u.get("name", "")}
            for u in raw.get("users", [])
        ],
    }
