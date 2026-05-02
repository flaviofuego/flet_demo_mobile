"""Unit tests for GetUsersUseCase."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core.utils.result import Failure, Success
from src.domain.entities.user import User
from src.domain.usecases.get_users import GetUsersUseCase


class TestGetUsersUseCase:
    def _make_use_case(self, users: list[User] | None = None) -> GetUsersUseCase:
        repo = MagicMock()
        repo.get_all.return_value = users or []
        return GetUsersUseCase(repository=repo)

    def test_returns_success_with_users(self) -> None:
        users = [User(id="1", name="Alice", email="alice@example.com")]
        use_case = self._make_use_case(users=users)

        result = use_case.execute()

        assert isinstance(result, Success)
        assert result.is_success is True
        assert result.value == users

    def test_returns_success_with_empty_list(self) -> None:
        use_case = self._make_use_case(users=[])
        result = use_case.execute()

        assert isinstance(result, Success)
        assert result.value == []

    def test_returns_failure_when_repository_raises(self) -> None:
        repo = MagicMock()
        repo.get_all.side_effect = RuntimeError("DB connection failed")
        use_case = GetUsersUseCase(repository=repo)

        result = use_case.execute()

        assert isinstance(result, Failure)
        assert result.is_failure is True
        assert "DB connection failed" in str(result.error)
