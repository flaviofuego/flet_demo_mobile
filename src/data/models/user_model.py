"""UserModel – the data-layer representation of a user.

Data models (DTOs) know how to serialise/deserialise themselves from raw
data formats such as JSON dictionaries.  They also know how to convert
themselves into the domain ``User`` entity and vice-versa.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.domain.entities.user import User


@dataclass
class UserModel:
    """Mutable data-transfer object for a user record.

    Attributes:
        id:    Unique identifier string.
        name:  Display name.
        email: E-mail address.
    """

    id: str
    name: str
    email: str

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserModel":
        """Create a ``UserModel`` from a plain dictionary."""
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            email=str(data["email"]),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialise this model to a plain dictionary."""
        return {"id": self.id, "name": self.name, "email": self.email}

    # ------------------------------------------------------------------
    # Domain conversion
    # ------------------------------------------------------------------

    @classmethod
    def from_entity(cls, user: User) -> "UserModel":
        """Create a ``UserModel`` from a domain :class:`~src.domain.entities.user.User`."""
        return cls(id=user.id, name=user.name, email=user.email)

    def to_entity(self) -> User:
        """Convert this model to the domain :class:`~src.domain.entities.user.User`."""
        return User(id=self.id, name=self.name, email=self.email)
