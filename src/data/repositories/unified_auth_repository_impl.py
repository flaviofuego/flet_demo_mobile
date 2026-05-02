from __future__ import annotations
from src.domain.models.auth_login_result import AuthLoginResult, AppUserRole
from src.domain.repositories.i_auth_repository import IAuthRepository
from src.domain.repositories.i_teacher_auth_repository import ITeacherAuthRepository
from src.domain.repositories.i_unified_auth_repository import IUnifiedAuthRepository


class UnifiedAuthRepositoryImpl(IUnifiedAuthRepository):
    """Tries teacher login first, then student login."""

    def __init__(
        self,
        student_auth: IAuthRepository,
        teacher_auth: ITeacherAuthRepository,
    ) -> None:
        self._student = student_auth
        self._teacher = teacher_auth

    def login_and_resolve(self, email: str, password: str) -> AuthLoginResult | None:
        teacher = self._teacher.login(email, password)
        if teacher is not None:
            self._student.logout()
            return AuthLoginResult(role=AppUserRole.teacher)

        student = self._student.login(email, password)
        if student is not None:
            self._teacher.logout()
            return AuthLoginResult(role=AppUserRole.student)

        return None
