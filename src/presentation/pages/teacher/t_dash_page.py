"""TDashPage — teacher dashboard."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER,
    TK_TEXT, TK_TEXT_FAINT, TK_GOLD, TK_GOLD_LIGHT,
    TK_SUCCESS, TK_DANGER,
)
from src.presentation.components.avatar_circle import avatar_circle
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def t_dash_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _stat_card(label: str, value: str, color: str) -> ft.Container:
        return ft.Container(
            bgcolor=TK_SURFACE, border_radius=14,
            border=ft.border.all(1, TK_BORDER),
            padding=14, expand=True,
            content=ft.Column(spacing=4, controls=[
                ft.Text(value, size=28, weight=ft.FontWeight.W_900, color=color),
                ft.Text(label, size=11, color=TK_TEXT_FAINT),
            ]),
        )

    def _eval_card(ev) -> ft.Container:
        active_color = TK_SUCCESS if ev.is_active else TK_TEXT_FAINT
        active_label = "Activa" if ev.is_active else "Cerrada"

        def _results(_) -> None:
            vm.load_group_results(ev)
            page.go("/teacher/results")

        def _rename(_) -> None:
            name_field = ft.TextField(value=ev.name, label="Nuevo nombre")
            def _confirm(_) -> None:
                try:
                    vm.rename_evaluation(ev.id, name_field.value or ev.name)
                    page.close(dlg)
                except Exception as e:
                    name_field.error_text = str(e)
                    page.update()
            dlg = ft.AlertDialog(
                title=ft.Text("Renombrar evaluación"),
                content=name_field,
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.close(dlg)),
                    ft.ElevatedButton("Guardar", on_click=_confirm),
                ],
            )
            page.open(dlg)

        def _delete(_) -> None:
            def _confirm(_) -> None:
                vm.delete_evaluation(ev.id)
                page.close(dlg)
            dlg = ft.AlertDialog(
                title=ft.Text("¿Eliminar evaluación?"),
                content=ft.Text(f"Se eliminará '{ev.name}' y todas sus respuestas."),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.close(dlg)),
                    ft.ElevatedButton("Eliminar",
                                     style=ft.ButtonStyle(bgcolor=TK_DANGER, color="#FFFFFF"),
                                     on_click=_confirm),
                ],
            )
            page.open(dlg)

        return ft.Container(
            bgcolor=TK_SURFACE, border_radius=14,
            border=ft.border.all(1, TK_BORDER),
            padding=14, margin=ft.margin.only(bottom=8),
            content=ft.Column(spacing=6, controls=[
                ft.Row(controls=[
                    ft.Column(expand=True, spacing=2, controls=[
                        ft.Text(ev.name, size=14, weight=ft.FontWeight.W_600, color=TK_TEXT),
                        ft.Text(ev.course_name or ev.category_name, size=11, color=TK_TEXT_FAINT),
                    ]),
                    ft.Container(
                        bgcolor=f"{active_color}22", border_radius=6,
                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                        content=ft.Text(active_label, size=10, color=active_color,
                                       weight=ft.FontWeight.W_600),
                    ),
                ]),
                ft.Row(spacing=8, controls=[
                    ft.TextButton("Resultados", on_click=_results),
                    ft.TextButton("Renombrar", on_click=_rename),
                    ft.TextButton("Eliminar",
                                 style=ft.ButtonStyle(color=TK_DANGER),
                                 on_click=_delete),
                ]),
            ]),
        )

    def _profile_sheet() -> ft.BottomSheet:
        t = vm.teacher
        initials = t.initials if t else "?"
        name     = t.name if t else ""
        email    = t.email if t else ""

        def _logout(_) -> None:
            page.close(bs)
            page.run_thread(lambda: (vm.logout(), page.go("/login")))

        bs = ft.BottomSheet(
            open=True,
            content=ft.Container(
                padding=24, bgcolor=TK_SURFACE,
                content=ft.Column(tight=True, controls=[
                    ft.Row(spacing=12, controls=[
                        avatar_circle(initials, size=48, bg_color=TK_GOLD, text_color=TK_BACKGROUND),
                        ft.Column(spacing=2, controls=[
                            ft.Text(name, size=16, weight=ft.FontWeight.W_600, color=TK_TEXT),
                            ft.Text(email, size=12, color=TK_TEXT_FAINT),
                        ]),
                    ]),
                    ft.Divider(color=TK_BORDER),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.LOGOUT, color=TK_DANGER),
                        title=ft.Text("Cerrar sesión", color=TK_DANGER),
                        on_click=_logout,
                    ),
                ]),
            ),
        )
        return bs

    def _build_body() -> ft.Control:
        if vm.is_loading:
            return ft.Container(expand=True, alignment=ft.alignment.center,
                               content=ft.ProgressRing(color=TK_GOLD))

        active_count = sum(1 for e in vm.evaluations if e.is_active)
        stats = ft.Row(spacing=8, controls=[
            _stat_card("Evaluaciones", str(len(vm.evaluations)), TK_GOLD),
            _stat_card("Activas", str(active_count), TK_SUCCESS),
            _stat_card("Grupos", str(vm.total_groups), TK_TEXT_FAINT),
        ])

        items: list[ft.Control] = [stats, ft.Container(height=8)]
        if vm.evaluations:
            items.append(ft.Text("EVALUACIONES", size=10, color=TK_TEXT_FAINT,
                                weight=ft.FontWeight.W_600, letter_spacing=1.2))
            items.extend(_eval_card(e) for e in vm.evaluations)

        return ft.ListView(controls=items, expand=True,
                          padding=ft.padding.symmetric(horizontal=16, vertical=12))

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify

    if not vm.is_logged_in:
        page.run_thread(vm.check_session)
    else:
        content.content = _build_body()

    nav = ft.NavigationBar(
        bgcolor=TK_SURFACE, indicator_color=TK_GOLD_LIGHT,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_OUTLINED, label="Inicio"),
            ft.NavigationBarDestination(icon=ft.Icons.UPLOAD_FILE_OUTLINED, label="Importar"),
            ft.NavigationBarDestination(icon=ft.Icons.BOOK_OUTLINED, label="Cursos"),
        ],
        on_change=lambda e: [
            page.go("/teacher/dash"),
            page.go("/teacher/profile"),
            page.go("/teacher/courses"),
        ][e.control.selected_index],
    )

    return ft.View(
        route="/teacher/dash",
        bgcolor=TK_BACKGROUND,
        navigation_bar=nav,
        appbar=ft.AppBar(
            title=ft.Text("Dashboard", color=TK_TEXT),
            bgcolor=TK_BACKGROUND, elevation=0,
            actions=[
                ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, icon_color=TK_GOLD,
                             tooltip="Nueva evaluación",
                             on_click=lambda _: page.go("/teacher/new-eval")),
                ft.IconButton(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, tooltip="Perfil",
                             on_click=lambda _: page.open(_profile_sheet())),
            ],
        ),
        controls=[content],
    )
