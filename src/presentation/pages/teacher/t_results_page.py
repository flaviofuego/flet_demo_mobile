"""TResultsPage — group results with drill-down."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER,
    TK_TEXT, TK_TEXT_FAINT, TK_GOLD, TK_SUCCESS, TK_WARNING, TK_DANGER,
    CRITERION_COLORS_DARK,
)
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


CRITERION_LABELS = ["PUNTU", "CONTRIB", "COMPRO", "ACTITU"]


def t_results_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _score_color(score: float) -> str:
        if score >= 4.0: return TK_SUCCESS
        if score >= 3.0: return TK_GOLD
        if score >= 2.5: return TK_WARNING
        return TK_DANGER

    def _criterion_ring(score: float, color: str, label: str) -> ft.Column:
        value = max(0.0, min(1.0, score / 5.0)) if score > 0 else 0.0
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            controls=[
                ft.Stack(
                    width=60, height=60,
                    controls=[
                        ft.ProgressRing(
                            value=value,
                            color=color,
                            bgcolor=f"#22{color[1:]}",
                            width=60, height=60,
                            stroke_width=5,
                        ),
                        ft.Container(
                            width=60, height=60,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(
                                f"{score:.1f}" if score > 0 else "—",
                                size=13, weight=ft.FontWeight.W_800,
                                color=color,
                            ),
                        ),
                    ],
                ),
                ft.Text(label, size=9, color=TK_TEXT_FAINT,
                        weight=ft.FontWeight.W_600,
                        text_align=ft.TextAlign.CENTER),
            ],
        )

    def _build_drill(group) -> ft.Control:
        def _back(_) -> None:
            vm.drill_group_index = None
            content.content = _build_body()
            page.update()

        rings_row = ft.Container(
            bgcolor=TK_SURFACE_ALT, border_radius=16, padding=18,
            margin=ft.margin.only(bottom=12),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                controls=[
                    _criterion_ring(group.criteria[i],
                                    CRITERION_COLORS_DARK[i],
                                    CRITERION_LABELS[i])
                    for i in range(len(group.criteria))
                ],
            ),
        )

        student_rows = [
            ft.Container(
                bgcolor=TK_SURFACE, border_radius=14,
                border=ft.Border.all(1, TK_BORDER),
                padding=ft.padding.symmetric(horizontal=14, vertical=12),
                margin=ft.margin.only(bottom=8),
                content=ft.Row(spacing=12, controls=[
                    ft.Container(
                        width=34, height=34,
                        border_radius=10,
                        bgcolor=f"#26{CRITERION_COLORS_DARK[i % 4][1:]}",
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            s.name[:2].upper(), size=11,
                            weight=ft.FontWeight.W_700,
                            color=CRITERION_COLORS_DARK[i % 4],
                        ),
                    ),
                    ft.Text(s.name, size=13, weight=ft.FontWeight.W_600,
                            color=TK_TEXT, expand=True),
                    ft.Text(f"{s.score:.1f}" if s.score > 0 else "—",
                            size=18, weight=ft.FontWeight.W_800,
                            color=_score_color(s.score)),
                ]),
            )
            for i, s in enumerate(group.students)
        ]

        back_btn = ft.GestureDetector(
            on_tap=_back,
            content=ft.Container(
                bgcolor=TK_SURFACE, border_radius=10,
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                content=ft.Row(spacing=4, tight=True, controls=[
                    ft.Icon(ft.Icons.CHEVRON_LEFT, size=16, color=TK_TEXT),
                    ft.Text("Volver", size=13, color=TK_TEXT),
                ]),
            ),
        )

        return ft.Column(expand=True, controls=[
            ft.Container(
                bgcolor=TK_SURFACE,
                padding=ft.padding.only(left=16, right=16, top=8, bottom=12),
                content=ft.Column(spacing=8, controls=[
                    back_btn,
                    ft.Text(group.name, size=20, weight=ft.FontWeight.W_700,
                            color=TK_TEXT),
                    ft.Text(f"Promedio: {group.average:.1f}"
                            if group.average > 0 else "Sin datos",
                            size=13, color=_score_color(group.average)),
                ]),
            ),
            ft.Divider(height=1, color=TK_BORDER),
            ft.ListView(
                expand=True,
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                controls=[
                    rings_row,
                    ft.Text("POR ESTUDIANTE", size=10, color=TK_TEXT_FAINT,
                            weight=ft.FontWeight.W_600),
                    ft.Container(height=6),
                    *student_rows,
                ],
            ),
        ])

    def _build_overview() -> ft.Control:
        if vm.results_loading:
            return ft.Container(expand=True, alignment=ft.Alignment(0, 0),
                                content=ft.ProgressRing(color=TK_GOLD))
        groups  = vm.group_results
        overall = vm.overall_average

        stats = ft.Row(spacing=8, controls=[
            ft.Container(
                expand=True, bgcolor=TK_SURFACE, border_radius=14,
                border=ft.Border.all(1, TK_BORDER), padding=14,
                content=ft.Column(spacing=6, controls=[
                    ft.Container(width=28, height=3, bgcolor=TK_GOLD,
                                 border_radius=2),
                    ft.Text(f"{overall:.1f}" if overall > 0 else "—",
                            size=26, weight=ft.FontWeight.W_900,
                            color=_score_color(overall) if overall > 0 else TK_TEXT_FAINT),
                    ft.Text("PROMEDIO\nGENERAL", size=10, color=TK_TEXT_FAINT,
                            weight=ft.FontWeight.W_600),
                ]),
            ),
            ft.Container(
                expand=True, bgcolor=TK_SURFACE, border_radius=14,
                border=ft.Border.all(1, TK_BORDER), padding=14,
                content=ft.Column(spacing=6, controls=[
                    ft.Text(str(len(groups)), size=26, weight=ft.FontWeight.W_900,
                            color=TK_SUCCESS),
                    ft.Text("GRUPOS", size=10, color=TK_TEXT_FAINT,
                            weight=ft.FontWeight.W_600),
                ]),
            ),
        ])

        if not groups:
            empty = ft.Container(
                bgcolor=TK_SURFACE, border_radius=14,
                border=ft.Border.all(1, TK_BORDER), padding=32,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.MONITOR_OUTLINED, size=48,
                                color=TK_TEXT_FAINT),
                        ft.Text("Sin respuestas aún", size=15,
                                weight=ft.FontWeight.W_600, color=TK_TEXT_FAINT),
                        ft.Text("Los resultados aparecerán cuando los estudiantes\n"
                                "envíen sus evaluaciones",
                                size=12, color=TK_TEXT_FAINT,
                                text_align=ft.TextAlign.CENTER),
                    ],
                ),
            )
            body_items: list[ft.Control] = [
                stats, ft.Container(height=12),
                ft.Text("GRUPOS — toca para detalle", size=10, color=TK_TEXT_FAINT,
                        weight=ft.FontWeight.W_600),
                ft.Container(height=8), empty,
            ]
        else:
            def _group_card(group, index: int) -> ft.Container:
                color = _score_color(group.average)
                def _drill(_) -> None:
                    vm.drill_group_index = index
                    content.content = _build_drill(group)
                    page.update()
                return ft.Container(
                    bgcolor=TK_SURFACE, border_radius=14,
                    border=ft.Border.all(1, TK_BORDER),
                    padding=14, margin=ft.margin.only(bottom=8),
                    on_click=_drill,
                    content=ft.Column(spacing=6, controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(group.name, size=14,
                                        weight=ft.FontWeight.W_600, color=TK_TEXT),
                                ft.Text(f"{group.average:.1f}"
                                        if group.average > 0 else "—",
                                        size=18, weight=ft.FontWeight.W_900,
                                        color=color),
                            ],
                        ),
                        ft.Text(f"{len(group.students)} miembros",
                                size=11, color=TK_TEXT_FAINT),
                        ft.ProgressBar(
                            value=max(0.0, min(1.0, (group.average - 2) / 3))
                            if group.average > 0 else 0,
                            bgcolor=f"#22{color[1:]}", color=color, height=6,
                        ),
                    ]),
                )

            body_items = [
                stats, ft.Container(height=12),
                ft.Text("GRUPOS — toca para detalle", size=10, color=TK_TEXT_FAINT,
                        weight=ft.FontWeight.W_600),
                ft.Container(height=8),
                *[_group_card(g, i) for i, g in enumerate(groups)],
            ]

        return ft.ListView(
            controls=body_items, expand=True,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )

    def _build_body() -> ft.Control:
        if vm.drill_group_index is not None and vm.group_results:
            return _build_drill(vm.group_results[vm.drill_group_index])
        return _build_overview()

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify
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

    eval_name = (vm.selected_eval_for_results.name
                 if vm.selected_eval_for_results else "Vista general")

    page_header = ft.Container(
        bgcolor=TK_SURFACE,
        padding=ft.padding.only(left=16, right=16, top=8, bottom=12),
        content=ft.Column(spacing=4, controls=[
            back_btn,
            ft.Text("Resultados", size=24, weight=ft.FontWeight.W_800, color=TK_TEXT),
            ft.Text(f"— {eval_name}", size=13, color=TK_TEXT_FAINT),
        ]),
    )

    return ft.View(
        route="/teacher/results",
        bgcolor=TK_BACKGROUND,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Column(expand=True, spacing=0,
                                  controls=[
                                      page_header,
                                      ft.Divider(height=1, color=TK_BORDER),
                                      content,
                                  ]),
            ),
        ],
    )
