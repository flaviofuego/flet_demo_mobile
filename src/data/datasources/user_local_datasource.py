"""In-memory local data source for users.

In a real application this would be backed by SQLite, SharedPreferences, or
another on-device store.  The in-memory implementation is used here to keep
the demo self-contained and easy to test.
"""

from __future__ import annotations

from src.data.models.user_model import UserModel


class UserLocalDataSource:
    """Stores and retrieves :class:`~src.data.models.user_model.UserModel`
    records from an in-memory list.

    Seed data is pre-loaded so the app shows content immediately.
    """

    def __init__(self) -> None:
        self._store: dict[str, UserModel] = {}
        self._seed()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _seed(self) -> None:
        """Populate the store with a few demo users."""
        demo_users = [
            UserModel(id="1", name="Alice Johnson", email="alice@example.com"),
            UserModel(id="2", name="Bob Smith", email="bob@example.com"),
            UserModel(id="3", name="Carol White", email="carol@example.com"),
        ]
        for user in demo_users:
            self._store[user.id] = user

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def get_all(self) -> list[UserModel]:
        """Return all stored user models."""
        return list(self._store.values())

    def get_by_id(self, user_id: str) -> UserModel | None:
        """Return the model with *user_id*, or ``None`` if absent."""
        return self._store.get(user_id)

    def save(self, model: UserModel) -> UserModel:
        """Persist *model* and return it."""
        self._store[model.id] = model
        return model

    def delete(self, user_id: str) -> bool:
        """Remove the record with *user_id*. Return ``True`` if it existed."""
        return self._store.pop(user_id, None) is not None
