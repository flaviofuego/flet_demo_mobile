"""Unit tests for HomeViewModel."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core.utils.result import Failure, Success
from src.core.error.exceptions import DataException
from src.domain.entities.user import User
from src.presentation.viewmodels.home_viewmodel import HomeViewModel


def _make_view_model(result) -> tuple[HomeViewModel, list]:
    """Return a HomeViewModel wired to return *result* from the use case."""
    use_case = MagicMock()
    use_case.execute.return_value = result

    notifications: list[str] = []
    vm = HomeViewModel(
        get_users_use_case=use_case,
        notify=lambda: notifications.append("notify"),
    )
    return vm, notifications


class TestHomeViewModel:
    def test_initial_state(self) -> None:
        use_case = MagicMock()
        vm = HomeViewModel(get_users_use_case=use_case)
        assert vm.users == []
        assert vm.is_loading is False
        assert vm.error_message == ""

    def test_load_users_success(self) -> None:
        users = [User(id="1", name="Alice", email="alice@example.com")]
        vm, notifications = _make_view_model(Success(users))

        vm.load_users()

        assert vm.users == users
        assert vm.is_loading is False
        assert vm.error_message == ""
        # Two notifications: one while loading, one after
        assert len(notifications) == 2

    def test_load_users_failure(self) -> None:
        error = DataException("network error")
        vm, notifications = _make_view_model(Failure(error))

        vm.load_users()

        assert vm.users == []
        assert vm.is_loading is False
        assert "network error" in vm.error_message

    def test_is_loading_resets_after_success(self) -> None:
        vm, _ = _make_view_model(Success([]))
        vm.load_users()
        assert vm.is_loading is False

    def test_is_loading_resets_after_failure(self) -> None:
        vm, _ = _make_view_model(Failure(DataException("err")))
        vm.load_users()
        assert vm.is_loading is False
