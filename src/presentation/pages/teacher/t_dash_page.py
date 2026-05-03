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


def t_dash_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _stat_card(label: str, value: str, color: str) -> ft.Container:
        return ft.Container(
            bgcolor=TK_SURFACE, border_radius=16,
            border=ft.Border.all(1, TK_BORDER),
            padding=14, expand=True,
            content=ft.Column(spacing=4, controls=[
                ft.Text(value, size=28, weight=ft.FontWeight.W_900, color=color),
                ft.Text(label, size=10, color=TK_TEXT_FAINT, weight=ft.FontWeight.W_600),
            ]),
        )

    def _eval_card(ev) -> ft.Container:
        active_color = TK_SUCCESS if ev.is_active else TK_TEXT_FAINT
        active_label = "Activa" if ev.is_active else "Cerrada"

        def _results(_) -> None:
            vm.load_group_results(ev)
            page.go("/teacher/results")

        def _rename(_) -> None:
            name_field = ft.TextField(value=ev.name, label="Nuevo nombre", focused_border_color=TK_GOLD)
            def _confirm(_) -> None:
                try:
                    vm.rename_evaluation(ev.id, name_field.value or ev.name)
                    page.pop_dialog()
                except Exception as e:
                    name_field.error_text = str(e)
                    page.update()
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("Renombrar evaluación"),
                content=name_field,
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                    ft.ElevatedButton("Guardar", on_click=_confirm,
                              style=ft.ButtonStyle(bgcolor=TK_GOLD, color=TK_BACKGROUND,
                                                   shape=ft.RoundedRectangleBorder(radius=10))),
                ],
            ))

        def _delete(_) -> None:
            def _confirm(_) -> None:
                vm.delete_evaluation(ev.id)
                page.pop_dialog()
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("¿Eliminar evaluación?"),
                content=ft.Text(f"Se eliminará '{ev.name}' y todas sus respuestas."),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                    ft.ElevatedButton("Eliminar",
                              style=ft.ButtonStyle(bgcolor=TK_DANGER, color="#FFFFFF",
                                                   shape=ft.RoundedRectangleBorder(radius=10)),
                              on_click=_confirm),
                ],
            ))

        return ft.Container(
            bgcolor=TK_SURFACE, border_radius=16,
            border=ft.Border.all(1, TK_BORDER),
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
                    ft.TextButton("Renombrar",  on_click=_rename),
                    ft.TextButton("Eliminar",
                                  style=ft.ButtonStyle(color=TK_DANGER),
                                  on_click=_delete),
                ]),
            ]),
        )

    def _profile_sheet() -> ft.BottomSheet:
        t        = vm.teacher
        initials = t.initials if t else "?"
        name     = t.name    if t else ""
        email    = t.email   if t else ""

        async def _logout(_) -> None:
            page.pop_dialog()
            vm.logout()
            await page.push_route("/login")

        return ft.BottomSheet(
            open=True,
            content=ft.Container(
                padding=24, bgcolor=TK_SURFACE,
                content=ft.Column(tight=True, controls=[
                    ft.Row(spacing=12, controls=[
                        avatar_circle(initials, size=48, bg_color=TK_GOLD, text_color=TK_BACKGROUND),
                        ft.Column(spacing=2, controls=[
                            ft.Text(name,  size=16, weight=ft.FontWeight.W_600, color=TK_TEXT),
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

    def _build_body() -> ft.Control:
        if vm.is_loading:
            return ft.Container(expand=True, alignment=ft.Alignment(0, 0),
                                content=ft.ProgressRing(color=TK_GOLD))

        active_count = sum(1 for e in vm.evaluations if e.is_active)
        stats = ft.Row(spacing=8, controls=[
            _stat_card("CATEGORÍAS", str(len(vm.categories)), TK_GOLD),
            _stat_card("ACTIVAS",    str(active_count),       TK_SUCCESS),
            _stat_card("GRUPOS",     str(vm.total_groups),    TK_TEXT_FAINT),
        ])

        section_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("MIS EVALUACIONES", size=11, color=TK_TEXT_FAINT, weight=ft.FontWeight.W_600),
                ft.Container(
                    on_click=lambda _: page.go("/teacher/new-eval"),
                    bgcolor=TK_GOLD, border_radius=20,
                    padding=ft.padding.symmetric(horizontal=14, vertical=6),
                    content=ft.Text("+ Nueva", size=13, color=TK_BACKGROUND, weight=ft.FontWeight.W_600),
                ),
            ],
        )

        if not vm.evaluations:
            empty = ft.Container(
                bgcolor=TK_SURFACE, border_radius=16,
                border=ft.Border.all(1, TK_BORDER), padding=32,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.INBOX_OUTLINED, size=48, color=TK_TEXT_FAINT),
                        ft.Text("Sin evaluaciones aún", size=15,
                                weight=ft.FontWeight.W_600, color=TK_TEXT_FAINT),
                        ft.Text("Importa grupos y crea tu primera evaluación.",
                                size=12, color=TK_TEXT_FAINT, text_align=ft.TextAlign.CENTER),
                    ],
                ),
            )
            items: list[ft.Control] = [
                stats, ft.Container(height=12),
                section_header, ft.Container(height=8), empty,
            ]
        else:
            items = [
                stats, ft.Container(height=12),
                section_header, ft.Container(height=8),
                *[_eval_card(e) for e in vm.evaluations],
            ]

        return ft.ListView(controls=items, expand=True,
                           padding=ft.padding.symmetric(horizontal=16, vertical=12))

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify

    t        = vm.teacher
    initials = t.initials if t else "?"
    name     = t.name    if t else ""

    header_col = ft.Column(spacing=2, controls=[
        ft.Text("Panel docente", size=12, color=TK_TEXT_FAINT),
        ft.Text(name, size=24, weight=ft.FontWeight.W_800, color=TK_TEXT),
    ])
    header_avatar = ft.GestureDetector(
        on_tap=lambda _: page.show_dialog(_profile_sheet()),
        content=avatar_circle(initials, size=40, bg_color=TK_GOLD, text_color=TK_BACKGROUND),
    )

    header = ft.Container(
        padding=ft.padding.only(left=16, right=16, top=8, bottom=4),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[header_col, header_avatar],
        ),
    )

    if not vm.is_logged_in:
        page.run_thread(vm.check_session)
    else:
        content.content = _build_body()

    return ft.View(
        route="/teacher/dash",
        bgcolor=TK_BACKGROUND,
        navigation_bar=_teacher_navbar(page, 0),
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Column(expand=True, spacing=0, controls=[header, content]),
            ),
        ],
    )
