"""TCourseManagePage — CRUD for teacher courses."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER,
    TK_TEXT, TK_TEXT_FAINT, TK_GOLD, TK_DANGER,
)
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def _pill_btn(text: str, on_tap, bg: str, fg: str, expand=False) -> ft.GestureDetector:
    return ft.GestureDetector(
        on_tap=on_tap,
        content=ft.Container(
            expand=expand, bgcolor=bg, border_radius=30,
            padding=ft.padding.symmetric(horizontal=20, vertical=13),
            alignment=ft.Alignment(0, 0),
            content=ft.Text(text, size=14, weight=ft.FontWeight.W_700,
                            color=fg, text_align=ft.TextAlign.CENTER),
        ),
    )


def t_course_manage_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _course_tile(course) -> ft.Container:
        def _delete(_) -> None:
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("¿Eliminar curso?"),
                content=ft.Text(f"'{course.name}' será eliminado."),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                    _pill_btn("Eliminar",
                              lambda _: (vm.delete_course(course.id), page.pop_dialog()),
                              TK_DANGER, "#FFFFFF"),
                ],
            ))
        return ft.Container(
            bgcolor=TK_SURFACE, border_radius=20,
            border=ft.Border.all(1, TK_BORDER),
            padding=14, margin=ft.margin.only(bottom=8),
            content=ft.Row(controls=[
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text(course.name, size=14, weight=ft.FontWeight.W_600, color=TK_TEXT),
                    ft.Text(course.code or "Sin código", size=11, color=TK_TEXT_FAINT),
                ]),
                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=TK_DANGER, on_click=_delete),
            ]),
        )

    def _add_sheet() -> ft.BottomSheet:
        nf = ft.TextField(
            label="Nombre", hint_text="Ej: Estructuras de Datos",
            autofocus=True, focused_border_color=TK_GOLD,
            border_color=TK_BORDER, bgcolor=TK_SURFACE_ALT, border_radius=12,
        )
        cf = ft.TextField(
            label="Código (opcional)", hint_text="Ej: DM2026-10",
            focused_border_color=TK_GOLD,
            border_color=TK_BORDER, bgcolor=TK_SURFACE_ALT, border_radius=12,
        )
        def _create(_) -> None:
            if not nf.value:
                nf.error_text = "Requerido"; page.update(); return
            vm.create_course(nf.value, cf.value or "")
            page.pop_dialog()
        return ft.BottomSheet(
            open=True,
            content=ft.Container(
                bgcolor=TK_SURFACE, padding=24,
                content=ft.Column(tight=True, spacing=16, controls=[
                    ft.Text("Nuevo curso", size=20, weight=ft.FontWeight.W_700, color=TK_TEXT),
                    ft.Column(spacing=6, controls=[
                        ft.Text("Nombre", size=12, color=TK_TEXT_FAINT),
                        nf,
                        ft.Text("Código (opcional)", size=12, color=TK_TEXT_FAINT),
                        cf,
                    ]),
                    _pill_btn("Crear curso", _create, TK_GOLD, TK_BACKGROUND, expand=True),
                ]),
            ),
        )

    def _build_body() -> ft.Control:
        if vm.is_loading:
            return ft.Container(expand=True, alignment=ft.Alignment(0, 0),
                                content=ft.ProgressRing(color=TK_GOLD))
        if not vm.courses:
            return ft.Container(
                expand=True, alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.SCHOOL_OUTLINED, size=56, color=TK_TEXT_FAINT),
                        ft.Text("Sin cursos creados", size=15,
                                weight=ft.FontWeight.W_600, color=TK_TEXT_FAINT),
                        ft.Text("Toca \"Nuevo\" para añadir tu primer curso",
                                size=12, color=TK_TEXT_FAINT, text_align=ft.TextAlign.CENTER),
                    ],
                ),
            )
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

    back_btn = ft.GestureDetector(
        on_tap=lambda _: page.go("/teacher/import"),
        content=ft.Container(
            bgcolor=TK_SURFACE, border_radius=20,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            content=ft.Row(spacing=4, tight=True, controls=[
                ft.Icon(ft.Icons.CHEVRON_LEFT, size=16, color=TK_TEXT),
                ft.Text("Volver", size=13, color=TK_TEXT),
            ]),
        ),
    )

    page_header = ft.Container(
        padding=ft.padding.only(left=16, right=16, top=8, bottom=4),
        content=ft.Column(spacing=8, controls=[
            back_btn,
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column(spacing=2, controls=[
                        ft.Text("Mis cursos", size=24, weight=ft.FontWeight.W_800, color=TK_TEXT),
                        ft.Text("Organiza tus evaluaciones por curso",
                                size=13, color=TK_TEXT_FAINT),
                    ]),
                    ft.GestureDetector(
                        on_tap=lambda _: page.show_dialog(_add_sheet()),
                        content=ft.Container(
                            bgcolor=TK_GOLD, border_radius=20,
                            padding=ft.padding.symmetric(horizontal=14, vertical=8),
                            content=ft.Text("+ Nuevo", size=13, color=TK_BACKGROUND,
                                            weight=ft.FontWeight.W_600),
                        ),
                    ),
                ],
            ),
        ]),
    )

    return ft.View(
        route="/teacher/courses",
        bgcolor=TK_BACKGROUND,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Column(expand=True, spacing=0,
                                  controls=[page_header, content]),
            ),
        ],
    )
