"""TImportPage — CSV import of groups."""
from __future__ import annotations
import os
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER,
    TK_TEXT, TK_TEXT_FAINT, TK_GOLD, TK_GOLD_LIGHT, TK_DANGER,
)
from src.presentation.components.avatar_circle import avatar_circle
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def _teacher_navbar(page: ft.Page, selected: int) -> ft.NavigationBar:
    return ft.NavigationBar(
        bgcolor=TK_SURFACE,
        indicator_color=TK_GOLD_LIGHT,
        selected_index=selected,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED,        label="INICIO"),
            ft.NavigationBarDestination(icon=ft.Icons.FACT_CHECK_OUTLINED,  label="EVALUAR"),
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART,            label="DATOS"),
            ft.NavigationBarDestination(icon=ft.Icons.UPLOAD_FILE_OUTLINED, label="IMPORTAR"),
        ],
        on_change=lambda e: page.go(
            ["/teacher/dash", "/teacher/new-eval", "/teacher/results", "/teacher/import"]
            [e.control.selected_index]
        ),
    )


def t_import_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content     = ft.Container(expand=True)
    error_text  = ft.Text("", color=TK_DANGER, size=12, visible=False)
    file_picker = ft.FilePicker()

    async def _pick_file(_) -> None:
        files = await file_picker.pick_files(
            allowed_extensions=["csv"], allow_multiple=False
        )
        if not files:
            return
        f        = files[0]
        cat_name = os.path.splitext(f.name)[0]
        try:
            with open(f.path, "r", encoding="utf-8-sig") as fh:
                csv_content = fh.read()
        except Exception as ex:
            error_text.value   = f"Error leyendo archivo: {ex}"
            error_text.visible = True
            page.update()
            return

        def _run() -> None:
            vm.import_csv(csv_content, cat_name, 0)
            if vm.import_error:
                error_text.value   = vm.import_error
                error_text.visible = True
            else:
                error_text.visible = False
            page.update()

        page.run_thread(_run)

    def _category_tile(cat) -> ft.Container:
        def _delete(_) -> None:
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("¿Eliminar categoría?"),
                content=ft.Text(f"'{cat.name}' y todos sus grupos serán eliminados."),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                    ft.ElevatedButton("Eliminar",
                              style=ft.ButtonStyle(bgcolor=TK_DANGER, color="#FFFFFF",
                                                   shape=ft.RoundedRectangleBorder(radius=10)),
                              on_click=lambda _: (vm.delete_category(cat.id), page.pop_dialog())),
                ],
            ))
        return ft.Container(
            bgcolor=TK_SURFACE, border_radius=16,
            border=ft.Border.all(1, TK_BORDER),
            padding=12, margin=ft.margin.only(bottom=8),
            content=ft.Row(controls=[
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text(cat.name, size=13, weight=ft.FontWeight.W_600, color=TK_TEXT),
                    ft.Text(f"{cat.group_count} grupos · {cat.member_count} miembros",
                            size=11, color=TK_TEXT_FAINT),
                ]),
                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=TK_DANGER, on_click=_delete),
            ]),
        )

    def _build_body() -> ft.Control:
        import_section = ft.Column(spacing=12, controls=[
            ft.ElevatedButton(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER, spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.ATTACH_FILE_ROUNDED, color=TK_BACKGROUND, size=18),
                        ft.Text("Importar CSV", size=15, weight=ft.FontWeight.W_600, color=TK_BACKGROUND),
                    ],
                ),
                expand=True,
                style=ft.ButtonStyle(
                    bgcolor=TK_GOLD, color=TK_BACKGROUND,
                    shape=ft.RoundedRectangleBorder(radius=30),
                    padding=ft.padding.symmetric(vertical=16),
                ),
                on_click=_pick_file,
                disabled=vm.import_loading,
            ),
            error_text,
        ])

        cats_section = ft.Column(spacing=8, controls=[
            ft.Container(height=8),
            ft.Text("CATEGORÍAS IMPORTADAS", size=10, weight=ft.FontWeight.W_600,
                    color=TK_TEXT_FAINT),
            *(
                [ft.Container(
                    bgcolor=TK_SURFACE, border_radius=16,
                    border=ft.Border.all(1, TK_BORDER), padding=32,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.FOLDER_OUTLINED, size=48, color=TK_TEXT_FAINT),
                            ft.Text("Sin categorías importadas", size=15,
                                    weight=ft.FontWeight.W_600, color=TK_TEXT_FAINT),
                            ft.Text("Usa el botón de arriba para cargar un CSV",
                                    size=12, color=TK_TEXT_FAINT, text_align=ft.TextAlign.CENTER),
                        ],
                    ),
                )]
                if not vm.categories
                else [_category_tile(c) for c in vm.categories]
            ),
        ])

        return ft.ListView(
            controls=[import_section, cats_section], expand=True,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify
    content.content = _build_body()

    t        = vm.teacher
    initials = t.initials if t else "?"
    name     = t.name    if t else ""
    email    = t.email   if t else ""

    header = ft.Container(
        padding=ft.padding.only(left=16, right=16, top=8, bottom=4),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(spacing=10, controls=[
                    avatar_circle(initials, size=36, bg_color=TK_GOLD, text_color=TK_BACKGROUND),
                    ft.Column(spacing=1, controls=[
                        ft.Text(name,  size=14, weight=ft.FontWeight.W_600, color=TK_TEXT),
                        ft.Text(email, size=11, color=TK_TEXT_FAINT),
                    ]),
                ]),
                ft.GestureDetector(
                    on_tap=lambda _: page.go("/teacher/courses"),
                    content=ft.Container(
                        bgcolor=TK_SURFACE_ALT, border_radius=20,
                        border=ft.Border.all(1, TK_BORDER),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        content=ft.Row(spacing=4, tight=True, controls=[
                            ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, size=14, color=TK_GOLD),
                            ft.Text("Cursos", size=13, color=TK_GOLD, weight=ft.FontWeight.W_500),
                        ]),
                    ),
                ),
            ],
        ),
    )

    title_block = ft.Container(
        padding=ft.padding.only(left=16, right=16, top=4, bottom=0),
        content=ft.Column(spacing=2, controls=[
            ft.Text("Importar grupos", size=24, weight=ft.FontWeight.W_800, color=TK_TEXT),
            ft.Text("Desde archivo CSV de Brightspace", size=13, color=TK_TEXT_FAINT),
        ]),
    )

    return ft.View(
        route="/teacher/import",
        bgcolor=TK_BACKGROUND,
        navigation_bar=_teacher_navbar(page, 3),
        services=[file_picker],
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Column(expand=True, spacing=0,
                                  controls=[header, title_block, content]),
            ),
        ],
    )
