"""Concrete implementation of :class:`~src.domain.repositories.user_repository.UserRepository`.

This class sits in the *data* layer and bridges the domain contract with the
local data source.  Its only job is to translate between ``UserModel`` (data
layer) and ``User`` (domain layer).
"""

from __future__ import annotations

from src.data.datasources.user_local_datasource import UserLocalDataSource
from src.data.models.user_model import UserModel
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class UserRepositoryImpl(UserRepository):
    """Implements :class:`UserRepository` using the local data source.

    Args:
        data_source: The concrete data source injected at construction time.
    """

    def __init__(self, data_source: UserLocalDataSource) -> None:
        self._data_source = data_source

    # ------------------------------------------------------------------
    # UserRepository interface
    # ------------------------------------------------------------------

    def get_all(self) -> list[User]:
        return [model.to_entity() for model in self._data_source.get_all()]

    def get_by_id(self, user_id: str) -> User | None:
        model = self._data_source.get_by_id(user_id)
        return model.to_entity() if model is not None else None

    def save(self, user: User) -> User:
        model = UserModel.from_entity(user)
        saved = self._data_source.save(model)
        return saved.to_entity()

    def delete(self, user_id: str) -> bool:
        return self._data_source.delete(user_id)
