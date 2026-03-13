"""Asynchronous Python client for TRMNL."""


class TRMNLError(Exception):
    """Generic exception."""


class TRMNLAuthenticationError(TRMNLError):
    """Authentication error."""
