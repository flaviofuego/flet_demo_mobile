from __future__ import annotations
from typing import Callable
from src.domain.models.auth_login_result import AuthLoginResult
from src.domain.repositories.i_unified_auth_repository import IUnifiedAuthRepository


class LoginViewModel:
    def __init__(
        self,
        unified_auth: IUnifiedAuthRepository,
        notify: Callable[[], None] | None = None,
    ) -> None:
        self._auth = unified_auth
        self._notify = notify or (lambda: None)
        self.is_loading: bool = False
        self.auth_error: str = ""

    def login(self, email: str, password: str) -> AuthLoginResult | None:
        if not email.strip() or not password:
            self.auth_error = "Completa todos los campos"
            self._notify()
            return None
        self.is_loading = True
        self.auth_error = ""
        self._notify()
        try:
            result = self._auth.login_and_resolve(email, password)
            if result is None:
                self.auth_error = "Correo o contraseña incorrectos"
                self._notify()
                return None
            return result
        except Exception:
            self.auth_error = "Error al conectar con la base de datos"
            self._notify()
            return None
        finally:
            self.is_loading = False
            self._notify()

    def clear_error(self) -> None:
        self.auth_error = ""
        self._notify()
