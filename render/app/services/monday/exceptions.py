"""Custom exceptions for Monday.com API interactions."""


class MondayAPIError(Exception):
    """Base exception for all Monday API errors."""

    def __init__(self, message: str, query: str = "", variables: dict = None, response_data: dict = None):
        super().__init__(message)
        self.query = query
        self.variables = variables or {}
        self.response_data = response_data or {}


class MondayAuthError(MondayAPIError):
    """Invalid API key or authentication failure."""


class MondayRateLimitError(MondayAPIError):
    """Rate limit exceeded."""

    def __init__(self, retry_after: float = 60.0, **kwargs):
        super().__init__(f"Rate limited. Retry after {retry_after}s", **kwargs)
        self.retry_after = retry_after


class MondayNotFoundError(MondayAPIError):
    """Requested resource not found."""


class MondayPermissionError(MondayAPIError):
    """Insufficient permissions."""


class MondayGraphQLError(MondayAPIError):
    """GraphQL query returned errors."""

    def __init__(self, errors: list[dict], **kwargs):
        messages = "; ".join(e.get("message", str(e)) for e in errors)
        super().__init__(f"GraphQL errors: {messages}", **kwargs)
        self.graphql_errors = errors


class MondayTimeoutError(MondayAPIError):
    """Request timed out."""


class MondayNetworkError(MondayAPIError):
    """Network connectivity error."""


class MondayValidationError(MondayAPIError):
    """Invalid query or variables."""
