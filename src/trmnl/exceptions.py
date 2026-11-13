"""Asynchronous Python client for TRMNL."""


class TRMNLError(Exception):
    """Generic exception."""


class TRMNLAuthenticationError(TRMNLError):
    """Authentication error."""


class TRMNLForbiddenError(TRMNLError):
    """The API key may not reach this resource."""


class TRMNLNotFoundError(TRMNLError):
    """The resource does not exist."""


class TRMNLRateLimitError(TRMNLError):
    """The API refused the request until a rate limit resets."""

    def __init__(self, message: str, retry_after: int | None) -> None:
        """Initialize with the seconds the server asked to wait, if it said."""
        super().__init__(message)
        self.retry_after = retry_after
