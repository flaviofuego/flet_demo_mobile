"""TNewEvalPage — create a new evaluation."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER,
    TK_TEXT, TK_TEXT_FAINT, TK_GOLD, TK_DANGER,
)
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def t_new_eval_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content = ft.Container(expand=True)

    name_field = ft.TextField(
        label="Nombre de la evaluación",
        value=vm.eval_name,
        focused_border_color=TK_GOLD,
        on_change=lambda e: setattr(vm, "eval_name", e.control.value),
    )
    error_text = ft.Text("", color=TK_DANGER, size=12, visible=False)

    HOUR_OPTIONS = [24, 48, 72, 96, 120, 168]
    VISIBILITY_OPTIONS = [("Privada", "private"), ("Pública", "public")]

    def _hours_chips() -> ft.Row:
        chips = []
        for h in HOUR_OPTIONS:
            selected = vm.selected_hours == h
            def _pick(_, hours=h):
                vm.selected_hours = hours
                _refresh()
            chips.append(ft.Container(
                on_click=_pick,
                bgcolor=TK_GOLD if selected else TK_SURFACE_ALT,
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                content=ft.Text(f"{h}h", size=12,
                               color=TK_BACKGROUND if selected else TK_TEXT_FAINT,
                               weight=ft.FontWeight.W_600),
            ))
        return ft.Row(wrap=True, spacing=6, controls=chips)

    def _vis_chips() -> ft.Row:
        chips = []
        for label, val in VISIBILITY_OPTIONS:
            selected = vm.selected_visibility == val
            def _pick(_, v=val):
                vm.selected_visibility = v
                _refresh()
            chips.append(ft.Container(
                on_click=_pick,
                bgcolor=TK_GOLD if selected else TK_SURFACE_ALT,
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                content=ft.Text(label, size=12,
                               color=TK_BACKGROUND if selected else TK_TEXT_FAINT,
                               weight=ft.FontWeight.W_600),
            ))
        return ft.Row(spacing=8, controls=chips)

    def _course_picker_sheet() -> ft.BottomSheet:
        def _pick(_, cid, cname):
            vm.selected_course_id = cid
            vm.selected_course_name = cname
            page.run_thread(lambda: vm.load_categories_for_course(cid))
            page.pop_dialog()

        tiles = [
            ft.ListTile(title=ft.Text(c.name, color=TK_TEXT),
                       on_click=lambda e, cid=c.id, cn=c.name: _pick(e, cid, cn))
            for c in vm.courses
        ]
        bs = ft.BottomSheet(
            open=True,
            content=ft.Container(bgcolor=TK_SURFACE, padding=16,
                                content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[
                                    ft.Text("Selecciona un curso", size=16,
                                           weight=ft.FontWeight.W_700, color=TK_TEXT),
                                    ft.Divider(color=TK_BORDER),
                                    *tiles,
                                ])),
        )
        return bs

    def _category_picker_sheet() -> ft.BottomSheet:
        def _pick(_, cid, cname):
            vm.selected_category_id   = cid
            vm.selected_category_name = cname
            page.pop_dialog()
            _refresh()

        cats = vm.categories_for_course
        tiles = [
            ft.ListTile(
                title=ft.Text(c.name, color=TK_TEXT),
                subtitle=ft.Text(f"{c.group_count} grupos · {c.member_count} miembros",
                               color=TK_TEXT_FAINT, size=11),
                on_click=lambda e, cid=c.id, cn=c.name: _pick(e, cid, cn),
            )
            for c in cats
        ]
        empty = [ft.Text("No hay categorías para este curso", color=TK_TEXT_FAINT)] if not cats else []
        bs = ft.BottomSheet(
            open=True,
            content=ft.Container(bgcolor=TK_SURFACE, padding=16,
                                content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[
                                    ft.Text("Selecciona categoría de grupos", size=16,
                                           weight=ft.FontWeight.W_700, color=TK_TEXT),
                                    ft.Divider(color=TK_BORDER),
                                    *empty, *tiles,
                                ])),
        )
        return bs

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
        return ft.ListView(
            controls=[
                ft.Text("NUEVA EVALUACIÓN", size=10, weight=ft.FontWeight.W_600,
                       color=TK_TEXT_FAINT),
                ft.Container(height=8),
                name_field,
                ft.Container(height=4),
                ft.Text("Curso", size=12, color=TK_TEXT_FAINT),
                ft.Button(
                    vm.selected_course_name or "Seleccionar curso",
                    style=ft.ButtonStyle(
                        bgcolor=TK_GOLD if vm.selected_course_name else TK_SURFACE_ALT,
                        color=TK_BACKGROUND if vm.selected_course_name else TK_TEXT,
                    ),
                    on_click=lambda _: page.show_dialog(_course_picker_sheet()),
                    expand=True,
                ),
                ft.Container(height=4),
                ft.Text("Grupos", size=12, color=TK_TEXT_FAINT),
                ft.Button(
                    vm.selected_category_name or "Seleccionar categoría",
                    style=ft.ButtonStyle(
                        bgcolor=TK_GOLD if vm.selected_category_name else TK_SURFACE_ALT,
                        color=TK_BACKGROUND if vm.selected_category_name else TK_TEXT,
                    ),
                    on_click=lambda _: page.show_dialog(_category_picker_sheet()),
                    expand=True,
                    disabled=vm.selected_course_id is None,
                ),
                ft.Container(height=4),
                ft.Text("Duración", size=12, color=TK_TEXT_FAINT),
                _hours_chips(),
                ft.Container(height=4),
                ft.Text("Visibilidad de resultados", size=12, color=TK_TEXT_FAINT),
                _vis_chips(),
                ft.Container(height=16),
                error_text,
                ft.Button(
                    "Creando..." if vm.is_loading else "Crear evaluación",
                    style=ft.ButtonStyle(bgcolor=TK_GOLD, color=TK_BACKGROUND),
                    expand=True,
                    disabled=vm.is_loading,
                    on_click=_on_create,
                ),
            ],
            expand=True,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )

    def _refresh() -> None:
        content.content = _build_body()
        page.update()

    def _notify() -> None:
        _refresh()

    vm._notify = _notify
    content.content = _build_body()

    return ft.View(
        route="/teacher/new-eval",
        bgcolor=TK_BACKGROUND,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK,
                                 on_click=lambda _: page.go("/teacher/dash")),
            title=ft.Text("Nueva evaluación", color=TK_TEXT),
            bgcolor=TK_BACKGROUND, elevation=0,
        ),
        controls=[content],
    )
