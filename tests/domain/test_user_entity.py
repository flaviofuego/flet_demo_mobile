"""Unit tests for domain entities."""

from __future__ import annotations

import pytest

from src.core.error.exceptions import ValidationException
from src.domain.entities.user import User


class TestUser:
    def test_valid_user_creation(self) -> None:
        user = User(id="1", name="Alice Johnson", email="alice@example.com")
        assert user.id == "1"
        assert user.name == "Alice Johnson"
        assert user.email == "alice@example.com"

    def test_display_name_is_title_cased(self) -> None:
        user = User(id="1", name="alice johnson", email="alice@example.com")
        assert user.display_name() == "Alice Johnson"

    def test_empty_id_raises(self) -> None:
        with pytest.raises(ValidationException, match="id must not be empty"):
            User(id="", name="Alice", email="alice@example.com")

    def test_blank_name_raises(self) -> None:
        with pytest.raises(ValidationException, match="name must not be blank"):
            User(id="1", name="   ", email="alice@example.com")

    def test_invalid_email_raises(self) -> None:
        with pytest.raises(ValidationException, match="email must contain"):
            User(id="1", name="Alice", email="not-an-email")

    def test_multiple_validation_errors_combined(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            User(id="", name="", email="bad")
        assert "id must not be empty" in str(exc_info.value)
        assert "name must not be blank" in str(exc_info.value)
        assert "email must contain" in str(exc_info.value)

    def test_user_is_immutable(self) -> None:
        user = User(id="1", name="Alice", email="alice@example.com")
        with pytest.raises((AttributeError, TypeError)):
            user.name = "Bob"  # type: ignore[misc]
