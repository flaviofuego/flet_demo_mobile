from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.models.teacher import Teacher


class ITeacherAuthRepository(ABC):

    @abstractmethod
    def login(self, email: str, password: str) -> Teacher | None: ...

    @abstractmethod
    def register(self, name: str, email: str, password: str) -> Teacher: ...

    @abstractmethod
    def logout(self) -> None: ...

    @abstractmethod
    def get_current_session(self) -> Teacher | None: ...
