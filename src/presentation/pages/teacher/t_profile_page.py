"""TProfilePage — teacher profile hub."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_BORDER, TK_TEXT, TK_TEXT_FAINT,
    TK_GOLD, TK_GOLD_LIGHT, TK_DANGER,
)
from src.presentation.pages.teacher.t_dash_page import _teacher_navbar
from src.presentation.components.avatar_circle import avatar_circle
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def t_profile_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    t = vm.teacher
    initials = t.initials if t else "?"
    name     = t.name if t else "—"
    email    = t.email if t else "—"

    async def _logout(_) -> None:
        vm.logout()
        await page.push_route("/login")

    nav = _teacher_navbar(page, 0)

    return ft.View(
        route="/teacher/profile",
        bgcolor=TK_BACKGROUND,
        navigation_bar=nav,
        controls=[
            ft.SafeArea(expand=True,
                       content=ft.ListView(
                           expand=True,
                           padding=ft.padding.symmetric(horizontal=16, vertical=24),
                           controls=[
                               ft.Row(spacing=16, controls=[
                                   avatar_circle(initials, size=64, bg_color=TK_GOLD, text_color=TK_BACKGROUND),
                                   ft.Column(spacing=4, controls=[
                                       ft.Text(name, size=18, weight=ft.FontWeight.W_700, color=TK_TEXT),
                                       ft.Text(email, size=12, color=TK_TEXT_FAINT),
                                       ft.Container(
                                           bgcolor=TK_GOLD_LIGHT, border_radius=6,
                                           padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                           content=ft.Text("Docente", size=10, color=TK_GOLD,
                                                          weight=ft.FontWeight.W_600),
                                       ),
                                   ]),
                               ]),
                               ft.Divider(color=TK_BORDER, height=32),
                               ft.ListTile(
                                   leading=ft.Icon(ft.Icons.UPLOAD_FILE_OUTLINED, color=TK_GOLD),
                                   title=ft.Text("Importar grupos CSV", color=TK_TEXT),
                                   subtitle=ft.Text("Formato Brightspace", color=TK_TEXT_FAINT, size=11),
                                   on_click=lambda _: page.go("/teacher/import"),
                               ),
                               ft.ListTile(
                                   leading=ft.Icon(ft.Icons.BOOK_OUTLINED, color=TK_GOLD),
                                   title=ft.Text("Gestionar cursos", color=TK_TEXT),
                                   on_click=lambda _: page.go("/teacher/courses"),
                               ),
                               ft.Divider(color=TK_BORDER),
                               ft.ListTile(
                                   leading=ft.Icon(ft.Icons.LOGOUT, color=TK_DANGER),
                                   title=ft.Text("Cerrar sesión", color=TK_DANGER),
                                   on_click=_logout,
                               ),
                           ],
                       )),
        ],
    )
