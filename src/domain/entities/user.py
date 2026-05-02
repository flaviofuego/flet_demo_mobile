"""User entity – the canonical domain representation of a user.

Domain entities contain *only* business rules; they have no knowledge of
databases, HTTP, or UI frameworks.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class User:
    """Immutable domain entity representing an application user.

    Attributes:
        id:    Unique identifier (e.g., UUID string or integer key).
        name:  Human-readable display name.
        email: Contact e-mail address.
    """

    id: str
    name: str
    email: str

    # ------------------------------------------------------------------
    # Domain validation
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        errors: list[str] = []
        if not self.id:
            errors.append("id must not be empty")
        if not self.name or not self.name.strip():
            errors.append("name must not be blank")
        if not self.email or "@" not in self.email:
            errors.append("email must contain '@'")
        if errors:
            from src.core.error.exceptions import ValidationException

            raise ValidationException("; ".join(errors))

    def display_name(self) -> str:
        """Return a formatted display name."""
        return self.name.strip().title()
