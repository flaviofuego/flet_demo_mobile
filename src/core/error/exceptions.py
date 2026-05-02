"""Application-level exception hierarchy.

All custom exceptions raised within the app inherit from ``AppException``
so that callers can catch errors at the desired level of granularity.
"""

from __future__ import annotations


class AppException(Exception):
    """Base class for all application exceptions."""

    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------


class DomainException(AppException):
    """Raised when a domain rule is violated."""


class EntityNotFoundException(DomainException):
    """Raised when a requested entity cannot be found."""


class ValidationException(DomainException):
    """Raised when entity validation fails."""


# ---------------------------------------------------------------------------
# Data / infrastructure exceptions
# ---------------------------------------------------------------------------


class DataException(AppException):
    """Raised when a data-layer operation fails."""


class NetworkException(DataException):
    """Raised on network / remote-API errors."""


class CacheException(DataException):
    """Raised on local-cache read/write errors."""
