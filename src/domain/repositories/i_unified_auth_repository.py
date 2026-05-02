from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.models.auth_login_result import AuthLoginResult


class IUnifiedAuthRepository(ABC):

    @abstractmethod
    def login_and_resolve(self, email: str, password: str) -> AuthLoginResult | None: ...
