"""Singleton Monday.com client."""

from app.core.config import get_settings
from app.services.monday.graphql import GraphQLExecutor

_client: GraphQLExecutor | None = None


def get_client() -> GraphQLExecutor:
    """Get the shared Monday GraphQL executor instance."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = GraphQLExecutor(
            api_key=settings.MONDAY_API_KEY,
            api_url=settings.MONDAY_API_URL,
        )
    return _client


def reset_client() -> None:
    """Reset the client (for testing)."""
    global _client
    _client = None
