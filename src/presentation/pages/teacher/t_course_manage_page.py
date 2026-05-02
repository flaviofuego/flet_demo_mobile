"""TCourseManagePage — CRUD for teacher courses."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_BORDER, TK_TEXT, TK_TEXT_FAINT,
    TK_GOLD, TK_GOLD_LIGHT, TK_DANGER,
)
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def t_course_manage_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _course_tile(course) -> ft.Container:
        def _delete(_) -> None:
            dlg = ft.AlertDialog(
                title=ft.Text("¿Eliminar curso?"),
                content=ft.Text(f"'{course.name}' será eliminado."),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.close(dlg)),
                    ft.ElevatedButton("Eliminar",
                                     style=ft.ButtonStyle(bgcolor=TK_DANGER, color="#FFFFFF"),
                                     on_click=lambda _: (vm.delete_course(course.id), page.close(dlg))),
                ],
            )
            page.open(dlg)
        return ft.Container(
            bgcolor=TK_SURFACE, border_radius=12,
            border=ft.border.all(1, TK_BORDER),
            padding=14, margin=ft.margin.only(bottom=8),
            content=ft.Row(controls=[
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text(course.name, size=14, weight=ft.FontWeight.W_600, color=TK_TEXT),
                    ft.Text(course.code or "Sin código", size=11, color=TK_TEXT_FAINT),
                ]),
                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=TK_DANGER, on_click=_delete),
            ]),
        )

    def _add_dialog() -> ft.AlertDialog:
        nf = ft.TextField(label="Nombre del curso", autofocus=True, focused_border_color=TK_GOLD)
        cf = ft.TextField(label="Código (opcional)", focused_border_color=TK_GOLD)
        def _create(_) -> None:
            if not nf.value:
                nf.error_text = "Requerido"; page.update(); return
            vm.create_course(nf.value, cf.value or "")
            page.close(dlg)
        dlg = ft.AlertDialog(
            title=ft.Text("Nuevo curso"),
            content=ft.Column(tight=True, controls=[nf, cf]),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.close(dlg)),
                ft.ElevatedButton("Crear", on_click=_create,
                                 style=ft.ButtonStyle(bgcolor=TK_GOLD, color=TK_BACKGROUND)),
            ],
        )
        return dlg

    def _build_body() -> ft.Control:
        if vm.is_loading:
            return ft.Container(expand=True, alignment=ft.alignment.center,
                               content=ft.ProgressRing(color=TK_GOLD))
        if not vm.courses:
            return ft.Container(expand=True, alignment=ft.alignment.center,
                               content=ft.Column(
                                   horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                   controls=[
                                       ft.Icon(ft.Icons.BOOK_OUTLINED, size=56, color=TK_TEXT_FAINT),
                                       ft.Text("Sin cursos. Crea el primero.", color=TK_TEXT_FAINT),
                                   ]))
        return ft.ListView(
            controls=[_course_tile(c) for c in vm.courses],
            expand=True,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify
    content.content = _build_body()

    nav = ft.NavigationBar(
        bgcolor=TK_SURFACE, indicator_color=TK_GOLD_LIGHT, selected_index=2,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_OUTLINED, label="Inicio"),
            ft.NavigationBarDestination(icon=ft.Icons.UPLOAD_FILE_OUTLINED, label="Importar"),
            ft.NavigationBarDestination(icon=ft.Icons.BOOK_OUTLINED, label="Cursos"),
        ],
        on_change=lambda e: [
            page.go("/teacher/dash"),
            page.go("/teacher/import"),
            page.go("/teacher/courses"),
        ][e.control.selected_index],
    )

    return ft.View(
        route="/teacher/courses",
        bgcolor=TK_BACKGROUND,
        navigation_bar=nav,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK,
                                 on_click=lambda _: page.go("/teacher/dash")),
            title=ft.Text("Cursos", color=TK_TEXT),
            bgcolor=TK_BACKGROUND, elevation=0,
            actions=[
                ft.IconButton(ft.Icons.ADD, icon_color=TK_GOLD, tooltip="Nuevo curso",
                             on_click=lambda _: page.open(_add_dialog())),
            ],
        ),
        controls=[content],
    )
