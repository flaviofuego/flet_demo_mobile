"""Login page — unified auth (teacher first, then student)."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_SURFACE_ALT, SK_BORDER,
    SK_TEXT, SK_TEXT_FAINT, SK_PRIMARY, SK_PRIMARY_LIGHT,
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT as TK_SURFACE_ALT_,
    TK_BORDER, TK_TEXT, TK_TEXT_FAINT, TK_GOLD, TK_GOLD_LIGHT, TK_DANGER,
)
from src.presentation.viewmodels.login_viewmodel import LoginViewModel
from src.presentation.viewmodels.student_viewmodel import StudentViewModel
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def login_page(
    page: ft.Page,
    login_vm: LoginViewModel,
    student_vm: StudentViewModel,
    teacher_vm: TeacherViewModel,
) -> ft.View:
    is_dark = [page.theme_mode == ft.ThemeMode.DARK]  # mutable via list

    def _is_dark() -> bool:
        return is_dark[0]

    def _accent() -> str:
        return TK_GOLD if _is_dark() else SK_PRIMARY

    email_field = ft.TextField(
        hint_text="Correo institucional",
        prefix_icon=ft.Icons.MAIL_OUTLINE_ROUNDED,
        focused_border_color=SK_PRIMARY,
    )
    password_field = ft.TextField(
        hint_text="Contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED,
        focused_border_color=SK_PRIMARY,
    )
    error_text = ft.Text("", color="#EF4444", size=12, visible=False)
    login_btn = ft.Button(
        "Iniciar sesión",
        expand=True,
        style=ft.ButtonStyle(bgcolor=SK_PRIMARY, color="#FFFFFF"),
    )
    register_btn = ft.OutlinedButton("Crear cuenta", expand=True)
    theme_btn = ft.IconButton(icon=ft.Icons.DARK_MODE_ROUNDED)

    def _notify() -> None:
        error_text.value = login_vm.auth_error
        error_text.visible = bool(login_vm.auth_error)
        login_btn.disabled = login_vm.is_loading
        login_btn.content = "Iniciando..." if login_vm.is_loading else "Iniciar sesión"
        page.update()

    login_vm._notify = _notify

    def _on_login(_) -> None:
        async def _do() -> None:
            result = login_vm.login(
                email_field.value or "", password_field.value or ""
            )
            if result is None:
                return
            if result.role.value == "teacher":
                teacher_vm.check_session()
                student_vm.student = None
            else:
                student_vm.check_session()
                teacher_vm.teacher = None
            await page.push_route(result.home_route)
        page.run_task(_do)

    def _on_register(_) -> None:
        login_vm.clear_error()
        page.go("/register")

    def _toggle_theme(_) -> None:
        is_dark[0] = not is_dark[0]
        page.theme_mode = ft.ThemeMode.DARK if is_dark[0] else ft.ThemeMode.LIGHT
        theme_btn.icon = (
            ft.Icons.LIGHT_MODE_ROUNDED if is_dark[0] else ft.Icons.DARK_MODE_ROUNDED
        )
        email_field.focused_border_color = _accent()
        password_field.focused_border_color = _accent()
        login_btn.style = ft.ButtonStyle(bgcolor=_accent(), color="#FFFFFF")
        view.bgcolor = TK_BACKGROUND if is_dark[0] else SK_BACKGROUND
        page.update()

    login_btn.on_click = _on_login
    register_btn.on_click = _on_register
    theme_btn.on_click = _toggle_theme

    view = ft.View(
        route="/login",
        bgcolor=SK_BACKGROUND,
        padding=24,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Container(
                    expand=True,
                    bgcolor=SK_SURFACE,
                    border_radius=18,
                    border=ft.Border.all(1, SK_BORDER),
                    padding=20,
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        expand=True,
                        spacing=10,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        width=44, height=44,
                                        bgcolor=SK_PRIMARY_LIGHT,
                                        border_radius=12,
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Icon(ft.Icons.SCHOOL_ROUNDED, color=SK_PRIMARY, size=24),
                                    ),
                                    ft.Container(expand=True),
                                    theme_btn,
                                ]
                            ),
                            ft.Text(
                                "Bienvenido a EvalUn",
                                size=24, weight=ft.FontWeight.W_800, color=SK_TEXT,
                            ),
                            ft.Container(height=4),
                            email_field,
                            password_field,
                            error_text,
                            login_btn,
                            ft.Text(
                                "¿No tienes cuenta?",
                                size=12, color=SK_TEXT_FAINT,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            register_btn,
                            ft.Container(height=4),
                            ft.Text(
                                "Autenticado por Roble SSO",
                                size=11, color=SK_TEXT_FAINT,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),
                ),
            )
        ],
    )
    return view
