"""Abstract repository contract for ``User`` persistence.

The domain layer defines *what* operations are needed; the data layer
provides the concrete implementation.  This inversion of dependencies
means the domain never imports from the data layer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.user import User


class UserRepository(ABC):
    """Contract for user storage and retrieval."""

    @abstractmethod
    def get_all(self) -> list[User]:
        """Return every user currently stored."""

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        """Return the user with *user_id*, or ``None`` if not found."""

    @abstractmethod
    def save(self, user: User) -> User:
        """Persist *user* and return the saved entity."""

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """Remove the user with *user_id*. Return ``True`` if deleted."""
