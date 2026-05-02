from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.models.student import Student


class IAuthRepository(ABC):

    @abstractmethod
    def login(self, email: str, password: str) -> Student | None: ...

    @abstractmethod
    def register(self, name: str, email: str, password: str) -> Student: ...

    @abstractmethod
    def logout(self) -> None: ...

    @abstractmethod
    def get_current_session(self) -> Student | None: ...
