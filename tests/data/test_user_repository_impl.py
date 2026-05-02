"""Unit tests for UserRepositoryImpl."""

from __future__ import annotations

import pytest

from src.data.datasources.user_local_datasource import UserLocalDataSource
from src.data.repositories.user_repository_impl import UserRepositoryImpl
from src.domain.entities.user import User


@pytest.fixture()
def repo() -> UserRepositoryImpl:
    """Fresh repository backed by a seeded in-memory data source."""
    return UserRepositoryImpl(data_source=UserLocalDataSource())


class TestUserRepositoryImpl:
    def test_get_all_returns_seeded_users(self, repo: UserRepositoryImpl) -> None:
        users = repo.get_all()
        assert len(users) == 3
        assert all(isinstance(u, User) for u in users)

    def test_get_by_id_returns_correct_user(self, repo: UserRepositoryImpl) -> None:
        user = repo.get_by_id("1")
        assert user is not None
        assert user.name == "Alice Johnson"

    def test_get_by_id_returns_none_for_missing(self, repo: UserRepositoryImpl) -> None:
        assert repo.get_by_id("999") is None

    def test_save_persists_new_user(self, repo: UserRepositoryImpl) -> None:
        new_user = User(id="100", name="Ivan Drago", email="ivan@example.com")
        saved = repo.save(new_user)
        assert saved == new_user
        assert repo.get_by_id("100") == new_user

    def test_delete_removes_existing_user(self, repo: UserRepositoryImpl) -> None:
        assert repo.delete("2") is True
        assert repo.get_by_id("2") is None

    def test_delete_returns_false_for_missing(self, repo: UserRepositoryImpl) -> None:
        assert repo.delete("999") is False
