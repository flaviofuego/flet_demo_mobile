"""TNewEvalPage — create a new evaluation."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER,
    TK_TEXT, TK_TEXT_FAINT, TK_GOLD, TK_DANGER,
)
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


HOUR_OPTIONS = [24, 48, 72, 168]


def t_new_eval_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content    = ft.Container(expand=True)
    error_text = ft.Text("", color=TK_DANGER, size=12, visible=False)
    name_field = ft.TextField(
        value=vm.eval_name,
        focused_border_color=TK_GOLD,
        border_color=TK_BORDER,
        bgcolor=TK_SURFACE,
        border_radius=13,
        on_change=lambda e: setattr(vm, "eval_name", e.control.value),
    )

    def _section_label(text: str) -> ft.Text:
        return ft.Text(text, size=10, weight=ft.FontWeight.W_600, color=TK_TEXT_FAINT)

    def _selector_row(label: str, on_tap, disabled=False) -> ft.Container:
        return ft.Container(
            bgcolor=TK_SURFACE, border_radius=13,
            border=ft.Border.all(1, TK_BORDER),
            padding=ft.padding.symmetric(horizontal=16, vertical=16),
            on_click=None if disabled else on_tap,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(label, color=TK_TEXT_FAINT, size=14),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TK_TEXT_FAINT, size=18),
                ],
            ),
        )

    def _course_picker_sheet() -> ft.BottomSheet:
        def _pick(cid, cname):
            vm.selected_course_id   = cid
            vm.selected_course_name = cname
            page.run_thread(lambda: vm.load_categories_for_course(cid))
            page.pop_dialog()

        if not vm.courses:
            tiles: list[ft.Control] = [ft.Container(
                padding=16,
                content=ft.Text("Sin cursos creados", color=TK_TEXT_FAINT,
                                 text_align=ft.TextAlign.CENTER),
            )]
        else:
            tiles = [
                ft.ListTile(
                    title=ft.Text(c.name, color=TK_TEXT),
                    on_click=lambda _, cid=c.id, cn=c.name: _pick(cid, cn),
                )
                for c in vm.courses
            ]
        return ft.BottomSheet(
            open=True,
            content=ft.Container(
                bgcolor=TK_SURFACE, padding=16,
                border_radius=ft.border_radius.only(top_left=20, top_right=20),
                content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[
                    ft.Text("Selecciona un curso", size=16,
                            weight=ft.FontWeight.W_700, color=TK_TEXT),
                    ft.Divider(color=TK_BORDER),
                    *tiles,
                ]),
            ),
        )

    def _category_picker_sheet() -> ft.BottomSheet:
        def _pick(cid, cname):
            vm.selected_category_id   = cid
            vm.selected_category_name = cname
            page.pop_dialog()
            _refresh()

        cats = vm.categories_for_course
        if not cats:
            tiles2: list[ft.Control] = [ft.Container(
                padding=16,
                content=ft.Text("No hay categorías para este curso",
                                 color=TK_TEXT_FAINT, text_align=ft.TextAlign.CENTER),
            )]
        else:
            tiles2 = [
                ft.ListTile(
                    title=ft.Text(c.name, color=TK_TEXT),
                    subtitle=ft.Text(f"{c.group_count} grupos · {c.member_count} miembros",
                                     color=TK_TEXT_FAINT, size=11),
                    on_click=lambda _, cid=c.id, cn=c.name: _pick(cid, cn),
                )
                for c in cats
            ]
        return ft.BottomSheet(
            open=True,
            content=ft.Container(
                bgcolor=TK_SURFACE, padding=16,
                border_radius=ft.border_radius.only(top_left=20, top_right=20),
                content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[
                    ft.Text("Categoría de grupos", size=16,
                            weight=ft.FontWeight.W_700, color=TK_TEXT),
                    ft.Divider(color=TK_BORDER),
                    *tiles2,
                ]),
            ),
        )

    def _pick_hour(h: int) -> None:
        vm.selected_hours = h
        _refresh()

    def _pick_vis(v: str) -> None:
        vm.selected_visibility = v
        _refresh()

    def _on_create(_) -> None:
        vm.eval_name = name_field.value or ""
        async def _run() -> None:
            err = vm.create_evaluation()
            if err:
                error_text.value   = err
                error_text.visible = True
                page.update()
            else:
                await page.push_route("/teacher/dash")
        page.run_task(_run)

    def _build_body() -> ft.Control:
        course_label = vm.selected_course_name or "Sin cursos creados"
        if vm.selected_course_id is None:
            cat_label = "Selecciona un curso primero"
        else:
            cat_label = vm.selected_category_name or "Selecciona una categoría"

        hours_chips = ft.Row(spacing=6, controls=[
            ft.GestureDetector(
                on_tap=lambda _, h=h: _pick_hour(h),
                content=ft.Container(
                    bgcolor=TK_GOLD if vm.selected_hours == h else TK_SURFACE_ALT,
                    border_radius=10,
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    content=ft.Text(
                        f"{h}h", size=13, weight=ft.FontWeight.W_600,
                        color=TK_BACKGROUND if vm.selected_hours == h else TK_TEXT_FAINT,
                    ),
                ),
            )
            for h in HOUR_OPTIONS
        ])

        def _vis_card(label: str, subtitle: str, icon, val: str) -> ft.Container:
            sel        = vm.selected_visibility == val
            icon_bg    = f"#33{TK_GOLD[1:]}" if sel else TK_SURFACE_ALT
            icon_color = TK_GOLD if sel else TK_TEXT_FAINT
            text_color = TK_GOLD if sel else TK_TEXT
            return ft.Container(
                bgcolor=TK_SURFACE, border_radius=13,
                border=ft.Border.all(1, TK_GOLD if sel else TK_BORDER),
                padding=14, margin=ft.margin.only(bottom=8),
                on_click=lambda _, v=val: _pick_vis(v),
                content=ft.Row(spacing=12, controls=[
                    ft.Container(
                        width=40, height=40, bgcolor=icon_bg,
                        border_radius=10, alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icon, color=icon_color, size=20),
                    ),
                    ft.Column(expand=True, spacing=2, controls=[
                        ft.Text(label,    size=14, weight=ft.FontWeight.W_600,
                                color=text_color),
                        ft.Text(subtitle, size=11, color=TK_TEXT_FAINT),
                    ]),
                ]),
            )

        hint = "Selecciona una categoría primero" if vm.selected_category_id is None else ""

        disabled = vm.is_loading or vm.selected_course_id is None or vm.selected_category_id is None
        launch_btn = ft.GestureDetector(
            on_tap=(lambda _: None) if disabled else _on_create,
            content=ft.Container(
                expand=True,
                bgcolor=f"#55{TK_GOLD[1:]}" if disabled else TK_GOLD,
                border_radius=14,
                padding=ft.padding.symmetric(vertical=14),
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "Creando..." if vm.is_loading else "Lanzar evaluación",
                    size=15, weight=ft.FontWeight.W_700,
                    color=TK_BACKGROUND, text_align=ft.TextAlign.CENTER,
                ),
            ),
        )

        return ft.ListView(
            expand=True,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            controls=[
                _section_label("NOMBRE"),
                ft.Container(height=4),
                name_field,
                ft.Container(height=18),
                _section_label("CURSO"),
                ft.Container(height=4),
                _selector_row(course_label,
                              lambda _: page.show_dialog(_course_picker_sheet())),
                ft.Container(height=18),
                _section_label("CATEGORÍA DE GRUPOS"),
                ft.Container(height=4),
                _selector_row(cat_label,
                              lambda _: page.show_dialog(_category_picker_sheet()),
                              disabled=vm.selected_course_id is None),
                ft.Container(height=18),
                _section_label("VENTANA DE TIEMPO"),
                ft.Container(height=6),
                hours_chips,
                ft.Container(height=18),
                _section_label("VISIBILIDAD DE RESULTADOS"),
                ft.Container(height=6),
                _vis_card("Pública",
                          "Estudiantes ven sus promedios recibidos por criterio",
                          ft.Icons.PEOPLE_OUTLINE, "public"),
                _vis_card("Privada",
                          "Solo el docente accede a los resultados detallados",
                          ft.Icons.LOCK_OUTLINE, "private"),
                ft.Container(height=8),
                error_text,
                launch_btn,
                ft.Container(height=4),
                ft.Text(hint, size=11, color=TK_TEXT_FAINT,
                        text_align=ft.TextAlign.CENTER, visible=bool(hint)),
            ],
        )

    def _refresh() -> None:
        content.content = _build_body()
        page.update()

    def _notify() -> None:
        _refresh()

    vm._notify = _notify
    vm.reset_eval_form()
    name_field.value = vm.eval_name
    content.content = _build_body()

    back_btn = ft.GestureDetector(
        on_tap=lambda _: page.go("/teacher/dash"),
        content=ft.Container(
            bgcolor=TK_SURFACE, border_radius=10,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            content=ft.Row(spacing=4, tight=True, controls=[
                ft.Icon(ft.Icons.CHEVRON_LEFT, size=16, color=TK_TEXT),
                ft.Text("Volver", size=13, color=TK_TEXT),
            ]),
        ),
    )

    page_header = ft.Container(
        bgcolor=TK_SURFACE,
        padding=ft.padding.only(left=16, right=16, top=8, bottom=12),
        content=ft.Column(spacing=8, controls=[
            back_btn,
            ft.Text("Nueva evaluación", size=24, weight=ft.FontWeight.W_800,
                    color=TK_TEXT),
        ]),
    )

    return ft.View(
        route="/teacher/new-eval",
        bgcolor=TK_BACKGROUND,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True, spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[
                        page_header,
                        ft.Divider(height=1, color=TK_BORDER),
                        content,
                    ]),
            ),
        ],
    )
