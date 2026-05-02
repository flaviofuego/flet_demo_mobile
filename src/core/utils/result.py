"""Result type – a lightweight Either monad for error handling.

Instead of raising exceptions at every layer boundary, functions can return a
``Result[T]`` that is either a ``Success`` (carrying a value of type ``T``) or
a ``Failure`` (carrying an :class:`~src.core.error.exceptions.AppException`).

Usage example::

    def divide(a: int, b: int) -> Result[float]:
        if b == 0:
            return Failure(ValidationException("Division by zero"))
        return Success(a / b)

    result = divide(10, 2)
    if result.is_success:
        print(result.value)   # 5.0
    else:
        print(result.error)   # AppException message
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from src.core.error.exceptions import AppException

T = TypeVar("T")


@dataclass(frozen=True)
class Success(Generic[T]):
    """Represents a successful computation."""

    value: T

    @property
    def is_success(self) -> bool:
        return True

    @property
    def is_failure(self) -> bool:
        return False

    @property
    def error(self) -> None:
        return None


@dataclass(frozen=True)
class Failure(Generic[T]):
    """Represents a failed computation."""

    error: AppException

    @property
    def is_success(self) -> bool:
        return False

    @property
    def is_failure(self) -> bool:
        return True

    @property
    def value(self) -> None:
        return None


# Union type alias used as the return type of fallible functions.
Result = Success[T] | Failure[T]
