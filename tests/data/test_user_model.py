"""Unit tests for UserModel."""

from __future__ import annotations

import pytest

from src.data.models.user_model import UserModel
from src.domain.entities.user import User


class TestUserModel:
    def test_from_dict(self) -> None:
        data = {"id": "42", "name": "Diana", "email": "diana@example.com"}
        model = UserModel.from_dict(data)
        assert model.id == "42"
        assert model.name == "Diana"
        assert model.email == "diana@example.com"

    def test_to_dict(self) -> None:
        model = UserModel(id="1", name="Eve", email="eve@example.com")
        d = model.to_dict()
        assert d == {"id": "1", "name": "Eve", "email": "eve@example.com"}

    def test_to_entity(self) -> None:
        model = UserModel(id="5", name="Frank", email="frank@example.com")
        user = model.to_entity()
        assert isinstance(user, User)
        assert user.id == "5"
        assert user.name == "Frank"
        assert user.email == "frank@example.com"

    def test_from_entity(self) -> None:
        user = User(id="7", name="Grace", email="grace@example.com")
        model = UserModel.from_entity(user)
        assert model.id == "7"
        assert model.name == "Grace"
        assert model.email == "grace@example.com"

    def test_roundtrip_entity_to_model_and_back(self) -> None:
        original = User(id="99", name="Hank", email="hank@example.com")
        model = UserModel.from_entity(original)
        restored = model.to_entity()
        assert original == restored
