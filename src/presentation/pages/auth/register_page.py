"""Register page — student or teacher registration."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_BORDER, SK_TEXT, SK_TEXT_FAINT,
    SK_PRIMARY, SK_PRIMARY_LIGHT,
)
from src.presentation.viewmodels.student_viewmodel import StudentViewModel
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def register_page(
    page: ft.Page,
    student_vm: StudentViewModel,
    teacher_vm: TeacherViewModel,
) -> ft.View:
    name_field = ft.TextField(
        hint_text="Nombre completo",
        prefix_icon=ft.Icons.PERSON_OUTLINE_ROUNDED,
        focused_border_color=SK_PRIMARY,
    )
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
    confirm_field = ft.TextField(
        hint_text="Confirmar contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED,
        focused_border_color=SK_PRIMARY,
    )
    error_text = ft.Text("", color="#EF4444", size=12, visible=False)
    role_tabs = ft.Tabs(
        tabs=[ft.Tab(text="Estudiante"), ft.Tab(text="Docente")],
        selected_index=0,
    )
    register_btn = ft.ElevatedButton(
        "Crear cuenta",
        expand=True,
        style=ft.ButtonStyle(bgcolor=SK_PRIMARY, color="#FFFFFF"),
    )

    def _show_error(msg: str) -> None:
        error_text.value = msg
        error_text.visible = True
        page.update()

    def _notify() -> None:
        vm = student_vm if role_tabs.selected_index == 0 else teacher_vm
        error_text.value = vm.auth_error
        error_text.visible = bool(vm.auth_error)
        register_btn.disabled = vm.is_loading
        register_btn.text = "Creando..." if vm.is_loading else "Crear cuenta"
        page.update()

    student_vm._notify = _notify
    teacher_vm._notify = _notify

    def _on_register(_) -> None:
        name     = name_field.value or ""
        email    = email_field.value or ""
        password = password_field.value or ""
        confirm  = confirm_field.value or ""
        if not name.strip() or not email.strip() or not password:
            _show_error("Completa todos los campos")
            return
        if password != confirm:
            _show_error("Las contraseñas no coinciden")
            return
        is_teacher = role_tabs.selected_index == 1

        def _do() -> None:
            if is_teacher:
                ok = teacher_vm.register(name, email, password)
                if ok:
                    page.go("/teacher/dash")
            else:
                ok = student_vm.register(name, email, password)
                if ok:
                    page.go("/student/courses")
        page.run_thread(_do)

    register_btn.on_click = _on_register

    return ft.View(
        route="/register",
        bgcolor=SK_BACKGROUND,
        padding=24,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/login")),
            title=ft.Text("Crear cuenta", color=SK_TEXT),
            bgcolor=SK_BACKGROUND,
            elevation=0,
        ),
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Container(
                    expand=True,
                    bgcolor=SK_SURFACE,
                    border_radius=18,
                    border=ft.border.all(1, SK_BORDER),
                    padding=20,
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        spacing=10,
                        controls=[
                            ft.Container(
                                width=44, height=44,
                                bgcolor=SK_PRIMARY_LIGHT,
                                border_radius=12,
                                alignment=ft.alignment.center,
                                content=ft.Icon(ft.Icons.SCHOOL_ROUNDED, color=SK_PRIMARY, size=24),
                            ),
                            ft.Text("Registro", size=22, weight=ft.FontWeight.W_700, color=SK_TEXT),
                            role_tabs,
                            name_field,
                            email_field,
                            password_field,
                            confirm_field,
                            error_text,
                            register_btn,
                        ],
                    ),
                ),
            )
        ],
    )
