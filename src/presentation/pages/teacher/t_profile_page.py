"""TProfilePage — teacher profile hub with groups accordion."""
from __future__ import annotations
import os
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER,
    TK_TEXT, TK_TEXT_MID, TK_TEXT_FAINT, TK_GOLD, TK_GOLD_LIGHT, TK_DANGER,
)
from src.presentation.pages.teacher.t_dash_page import _teacher_navbar
from src.presentation.components.teacher_avatar import teacher_avatar
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def t_profile_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content     = ft.Container(expand=True)
    error_text  = ft.Text("", color=TK_DANGER, size=12, visible=False)
    file_picker = ft.FilePicker()
    _expanded: dict[int, bool] = {}

    t        = vm.teacher
    initials = t.initials if t else "?"
    name     = t.name    if t else "—"
    email    = t.email   if t else "—"

    async def _pick_file(_) -> None:
        files = await file_picker.pick_files(
            allowed_extensions=["csv"], allow_multiple=False
        )
        if not files:
            return
        f = files[0]
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

    def _group_row(group) -> ft.Container:
        return ft.Container(
            padding=ft.padding.only(left=14, top=10, right=14, bottom=10),
            content=ft.Column(spacing=6, controls=[
                ft.Row(controls=[
                    ft.Icon(ft.Icons.GROUP_OUTLINED, size=14, color=TK_GOLD),
                    ft.Container(width=6),
                    ft.Text(group.name, size=12, weight=ft.FontWeight.W_700,
                            color=TK_TEXT, expand=True),
                    ft.Text(f"{len(group.members)} estudiantes",
                            size=10, color=TK_TEXT_FAINT),
                ]),
                *[ft.Container(
                    padding=ft.padding.only(left=20, bottom=3),
                    content=ft.Text(m.name.title(), size=11, color=TK_TEXT_MID),
                ) for m in group.members],
            ]),
        )

    def _category_tile(cat) -> ft.Container:
        is_open  = _expanded.get(cat.id, False)
        date_str = (f"{cat.imported_at.day}/{cat.imported_at.month}"
                    f"/{cat.imported_at.year}")

        def _toggle(_) -> None:
            _expanded[cat.id] = not _expanded.get(cat.id, False)
            content.content = _build_body()
            page.update()

        def _delete(_) -> None:
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("¿Eliminar categoría?"),
                content=ft.Text(
                    f"'{cat.name}' y todos sus grupos serán eliminados."),
                actions=[
                    ft.TextButton("Cancelar",
                                  on_click=lambda _: page.pop_dialog()),
                    ft.GestureDetector(
                        on_tap=lambda _: (vm.delete_category(cat.id),
                                          page.pop_dialog()),
                        content=ft.Container(
                            bgcolor=TK_DANGER, border_radius=14,
                            padding=ft.padding.symmetric(horizontal=16, vertical=10),
                            content=ft.Text("Eliminar", size=13,
                                            weight=ft.FontWeight.W_700,
                                            color="#FFFFFF"),
                        ),
                    ),
                ],
            ))

        header = ft.GestureDetector(
            on_tap=_toggle,
            content=ft.Container(
                padding=14,
                content=ft.Row(controls=[
                    ft.Icon(
                        ft.Icons.KEYBOARD_ARROW_UP_ROUNDED if is_open
                        else ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED,
                        size=20, color=TK_TEXT_FAINT,
                    ),
                    ft.Container(width=8),
                    ft.Column(expand=True, spacing=2, controls=[
                        ft.Text(cat.name, size=13, weight=ft.FontWeight.W_700,
                                color=TK_TEXT),
                        ft.Text(
                            f"{cat.group_count} grupos · "
                            f"{cat.member_count} estudiantes · {date_str}",
                            size=11, color=TK_TEXT_FAINT,
                        ),
                    ]),
                    ft.Container(width=8),
                    ft.GestureDetector(
                        on_tap=_delete,
                        content=ft.Container(
                            padding=6, bgcolor=f"#1A{TK_DANGER[1:]}",
                            border_radius=8,
                            content=ft.Icon(ft.Icons.DELETE_OUTLINE_ROUNDED,
                                            size=16, color=TK_DANGER),
                        ),
                    ),
                ]),
            ),
        )

        body: list[ft.Control] = [header]
        if is_open and cat.groups:
            body.append(ft.Divider(height=1, color=TK_BORDER))
            for g in cat.groups:
                body.append(_group_row(g))

        return ft.Container(
            bgcolor=TK_SURFACE, border_radius=14,
            border=ft.Border.all(1, TK_BORDER),
            margin=ft.margin.only(bottom=8),
            content=ft.Column(spacing=0, controls=body),
        )

    def _build_body() -> ft.Control:
        import_btn = ft.GestureDetector(
            on_tap=(lambda _: None) if vm.import_loading else _pick_file,
            content=ft.Container(
                expand=True,
                bgcolor=f"#88{TK_GOLD[1:]}" if vm.import_loading else TK_GOLD,
                border_radius=14,
                padding=ft.padding.symmetric(vertical=14),
                alignment=ft.Alignment(0, 0),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER, spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.UPLOAD_FILE_ROUNDED,
                                color=TK_BACKGROUND, size=16),
                        ft.Text(
                            "Importando..." if vm.import_loading
                            else "Importar CSV",
                            size=13, weight=ft.FontWeight.W_700,
                            color=TK_BACKGROUND,
                        ),
                    ],
                ),
            ),
        )

        if not vm.categories:
            cats_content: list[ft.Control] = [
                ft.Container(
                    bgcolor=TK_SURFACE, border_radius=14,
                    border=ft.Border.all(1, TK_BORDER), padding=32,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.FOLDER_OUTLINED, size=48,
                                    color=TK_TEXT_FAINT),
                            ft.Text("Sin grupos importados", size=15,
                                    weight=ft.FontWeight.W_600,
                                    color=TK_TEXT_FAINT),
                            ft.Text("Importa un CSV para ver tus grupos aquí",
                                    size=12, color=TK_TEXT_FAINT,
                                    text_align=ft.TextAlign.CENTER),
                        ],
                    ),
                )
            ]
        else:
            cats_content = [_category_tile(c) for c in vm.categories]

        return ft.ListView(
            expand=True,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            controls=[
                import_btn,
                error_text,
                ft.Container(height=16),
                ft.Text("GRUPOS", size=11, weight=ft.FontWeight.W_700,
                        color=TK_TEXT_FAINT),
                ft.Container(height=8),
                *cats_content,
            ],
        )

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify
    content.content = _build_body()

    async def _logout(_) -> None:
        vm.logout()
        await page.push_route("/login")

    header = ft.Container(
        bgcolor=TK_SURFACE,
        padding=ft.padding.only(left=16, right=16, top=12, bottom=12),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(spacing=12, controls=[
                    teacher_avatar(initials, size=52),
                    ft.Column(spacing=2, controls=[
                        ft.Text(name,  size=17, weight=ft.FontWeight.W_800,
                                color=TK_TEXT),
                        ft.Text(email, size=11, color=TK_TEXT_FAINT),
                    ]),
                ]),
                ft.GestureDetector(
                    on_tap=_logout,
                    content=ft.Container(
                        bgcolor=f"#1A{TK_DANGER[1:]}",
                        border_radius=10,
                        border=ft.Border.all(1, f"#4D{TK_DANGER[1:]}"),
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        content=ft.Row(spacing=5, tight=True, controls=[
                            ft.Icon(ft.Icons.LOGOUT_ROUNDED, size=13,
                                    color=TK_DANGER),
                            ft.Text("Salir", size=12,
                                    weight=ft.FontWeight.W_700, color=TK_DANGER),
                        ]),
                    ),
                ),
            ],
        ),
    )

    return ft.View(
        route="/teacher/profile",
        bgcolor=TK_BACKGROUND,
        navigation_bar=_teacher_navbar(page, 0),
        services=[file_picker],
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Column(expand=True, spacing=0, controls=[
                    header,
                    ft.Divider(height=1, color=TK_BORDER),
                    content,
                ]),
            ),
        ],
    )
