"""TDashPage — teacher dashboard."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER,
    TK_TEXT, TK_TEXT_FAINT, TK_GOLD, TK_GOLD_LIGHT, TK_GOLD_BORDER,
    TK_SUCCESS, TK_DANGER,
)
from src.presentation.components.teacher_avatar import teacher_avatar
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
            bgcolor=TK_SURFACE_ALT, border_radius=14,
            border=ft.Border.all(1, TK_BORDER),
            padding=14, expand=True,
            content=ft.Column(spacing=4, controls=[
                ft.Text(value, size=26, weight=ft.FontWeight.W_900, color=color),
                ft.Text(label, size=10, color=TK_TEXT_FAINT, weight=ft.FontWeight.W_600),
            ]),
        )

    def _active_hero() -> ft.Control:
        active = next((e for e in vm.evaluations if e.is_active), None)
        if active is None:
            return ft.Container(height=0)
        return ft.Container(
            bgcolor=TK_GOLD_LIGHT,
            border_radius=16,
            border=ft.Border.all(1, TK_GOLD_BORDER),
            padding=16,
            margin=ft.margin.only(bottom=12),
            content=ft.Column(spacing=6, controls=[
                ft.Row(spacing=8, controls=[
                    ft.Container(width=8, height=8, border_radius=4, bgcolor=TK_GOLD),
                    ft.Text("Evaluación activa", size=10,
                            weight=ft.FontWeight.W_700, color=TK_GOLD),
                ]),
                ft.Text(active.name, size=15, weight=ft.FontWeight.W_800, color=TK_TEXT),
                ft.Text(active.course_name or active.category_name,
                        size=11, color=TK_TEXT_FAINT),
                ft.GestureDetector(
                    on_tap=lambda _: (vm.load_group_results(active),
                                      page.go("/teacher/results")),
                    content=ft.Container(
                        bgcolor=TK_GOLD, border_radius=10,
                        padding=ft.padding.symmetric(horizontal=14, vertical=8),
                        content=ft.Text("Ver resultados", size=12,
                                        weight=ft.FontWeight.W_700,
                                        color=TK_BACKGROUND),
                    ),
                ),
            ]),
        )

    def _eval_card(ev) -> ft.Container:
        active_color = TK_SUCCESS if ev.is_active else TK_TEXT_FAINT
        active_label = "Activa" if ev.is_active else "Cerrada"

        def _results(_) -> None:
            vm.load_group_results(ev)
            page.go("/teacher/results")

        def _rename(_) -> None:
            name_field = ft.TextField(value=ev.name, label="Nuevo nombre",
                                      focused_border_color=TK_GOLD)
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
                    ft.GestureDetector(
                        on_tap=_confirm,
                        content=ft.Container(
                            bgcolor=TK_GOLD, border_radius=10,
                            padding=ft.padding.symmetric(horizontal=16, vertical=10),
                            content=ft.Text("Guardar", size=13,
                                            weight=ft.FontWeight.W_700,
                                            color=TK_BACKGROUND),
                        ),
                    ),
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
                    ft.GestureDetector(
                        on_tap=_confirm,
                        content=ft.Container(
                            bgcolor=TK_DANGER, border_radius=10,
                            padding=ft.padding.symmetric(horizontal=16, vertical=10),
                            content=ft.Text("Eliminar", size=13,
                                            weight=ft.FontWeight.W_700,
                                            color="#FFFFFF"),
                        ),
                    ),
                ],
            ))

        return ft.Container(
            bgcolor=TK_SURFACE, border_radius=14,
            border=ft.Border.all(1, TK_BORDER),
            padding=14, margin=ft.margin.only(bottom=8),
            content=ft.Column(spacing=6, controls=[
                ft.Row(controls=[
                    ft.Column(expand=True, spacing=2, controls=[
                        ft.Text(ev.name, size=14, weight=ft.FontWeight.W_600, color=TK_TEXT),
                        ft.Text(ev.course_name or ev.category_name,
                                size=11, color=TK_TEXT_FAINT),
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
                border_radius=ft.border_radius.only(top_left=20, top_right=20),
                content=ft.Column(tight=True, controls=[
                    ft.Row(spacing=12, controls=[
                        teacher_avatar(initials, size=48),
                        ft.Column(spacing=2, controls=[
                            ft.Text(name,  size=16, weight=ft.FontWeight.W_600, color=TK_TEXT),
                            ft.Text(email, size=12, color=TK_TEXT_FAINT),
                        ]),
                    ]),
                    ft.Divider(color=TK_BORDER),
                    ft.GestureDetector(
                        on_tap=_logout,
                        content=ft.Container(
                            expand=True,
                            bgcolor=f"#33{TK_DANGER[1:]}",
                            border_radius=14,
                            border=ft.Border.all(1, f"#99{TK_DANGER[1:]}"),
                            padding=ft.padding.symmetric(vertical=14),
                            alignment=ft.Alignment(0, 0),
                            content=ft.Row(
                                spacing=8,
                                alignment=ft.MainAxisAlignment.CENTER,
                                tight=True,
                                controls=[
                                    ft.Icon(ft.Icons.LOGOUT_ROUNDED,
                                            size=16, color=TK_DANGER),
                                    ft.Text("Cerrar sesión", size=14,
                                            weight=ft.FontWeight.W_700,
                                            color=TK_DANGER),
                                ],
                            ),
                        ),
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
                ft.Text("MIS EVALUACIONES", size=11, color=TK_TEXT_FAINT,
                        weight=ft.FontWeight.W_600),
                ft.GestureDetector(
                    on_tap=lambda _: page.go("/teacher/new-eval"),
                    content=ft.Container(
                        bgcolor=TK_GOLD, border_radius=10,
                        padding=ft.padding.symmetric(horizontal=14, vertical=6),
                        content=ft.Text("+ Nueva", size=13, color=TK_BACKGROUND,
                                        weight=ft.FontWeight.W_600),
                    ),
                ),
            ],
        )

        if not vm.evaluations:
            empty = ft.Container(
                bgcolor=TK_SURFACE, border_radius=14,
                border=ft.Border.all(1, TK_BORDER), padding=32,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.INBOX_OUTLINED, size=48, color=TK_TEXT_FAINT),
                        ft.Text("Sin evaluaciones aún", size=15,
                                weight=ft.FontWeight.W_600, color=TK_TEXT_FAINT),
                        ft.Text("Importa grupos y crea tu primera evaluación.",
                                size=12, color=TK_TEXT_FAINT,
                                text_align=ft.TextAlign.CENTER),
                    ],
                ),
            )
            items: list[ft.Control] = [
                stats, ft.Container(height=12),
                _active_hero(),
                section_header, ft.Container(height=8), empty,
            ]
        else:
            items = [
                stats, ft.Container(height=12),
                _active_hero(),
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
        content=teacher_avatar(initials, size=40),
    )

    header = ft.Container(
        bgcolor=TK_SURFACE,
        padding=ft.padding.only(left=16, right=16, top=8, bottom=12),
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
                content=ft.Column(
                    expand=True, spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[
                        header,
                        ft.Divider(height=1, color=TK_BORDER),
                        content,
                    ]),
            ),
        ],
    )
