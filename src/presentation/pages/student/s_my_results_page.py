"""SMyResultsPage — student's evaluation results."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_SURFACE_ALT, SK_BORDER,
    SK_TEXT, SK_TEXT_FAINT, SK_PRIMARY, CRITERION_COLORS,
)
from src.presentation.viewmodels.student_viewmodel import StudentViewModel

_SK_SUCCESS = "#059669"


def s_my_results_page(page: ft.Page, vm: StudentViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _score_color(avg: float) -> str:
        if avg >= 4.0: return _SK_SUCCESS
        if avg >= 3.0: return SK_PRIMARY
        if avg >= 2.5: return "#F59E0B"
        return "#EF4444"

    def _criterion_card(label: str, score: float, color: str) -> ft.Container:
        bar_val = max(0.0, min(1.0, (score - 1) / 4)) if score > 0 else 0.0
        return ft.Container(
            bgcolor=SK_SURFACE, border_radius=14,
            border=ft.Border.all(1, SK_BORDER),
            padding=14, margin=ft.margin.only(bottom=10),
            content=ft.Column(spacing=8, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(spacing=8, controls=[
                            ft.Container(width=4, height=28, bgcolor=color,
                                         border_radius=2),
                            ft.Text(label, size=13, weight=ft.FontWeight.W_700,
                                    color=SK_TEXT),
                        ]),
                        ft.Text(f"{score:.1f}" if score > 0 else "—",
                                size=20, weight=ft.FontWeight.W_800, color=color),
                    ],
                ),
                ft.ProgressBar(
                    value=bar_val,
                    bgcolor=SK_BORDER,
                    color=color,
                    height=5,
                    border_radius=ft.border_radius.all(99),
                ),
            ]),
        )

    def _build_body() -> ft.Control:
        results = vm.my_results
        ev      = vm.active_eval
        avg     = vm.my_average
        vis_label = ""
        if ev:
            vis_label = ("Resultados visibles" if ev.visibility == "public"
                         else "Resultados privados")

        if not results or avg == 0:
            return ft.Container(expand=True, alignment=ft.Alignment(0, 0),
                               content=ft.Column(
                                   horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                   controls=[
                                       ft.Icon(ft.Icons.PENDING_OUTLINED, size=56,
                                               color=SK_TEXT_FAINT),
                                       ft.Text("Resultados pendientes",
                                               color=SK_TEXT_FAINT),
                                       ft.Text(
                                           "Completa tu evaluación para ver resultados",
                                           size=12, color=SK_TEXT_FAINT,
                                           text_align=ft.TextAlign.CENTER),
                                   ]))

        avg_color = _score_color(avg)
        perf = ("Excelente" if avg >= 4.5 else "Muy bueno" if avg >= 4.0
                else "Bueno" if avg >= 3.0 else "Regular")

        avg_card = ft.Container(
            bgcolor=SK_SURFACE_ALT, border_radius=18,
            padding=ft.padding.symmetric(horizontal=20, vertical=24),
            margin=ft.margin.only(bottom=16),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4,
                controls=[
                    ft.Text(f"{avg:.1f}" if avg > 0 else "—",
                            size=52, weight=ft.FontWeight.W_800, color=avg_color),
                    ft.Text("Promedio general", size=12, color=SK_TEXT_FAINT),
                    ft.Container(
                        bgcolor=f"{_SK_SUCCESS}17",
                        border_radius=10,
                        border=ft.Border.all(1, f"{_SK_SUCCESS}4D"),
                        padding=ft.padding.symmetric(horizontal=16, vertical=8),
                        content=ft.Text(perf, size=12, weight=ft.FontWeight.W_700,
                                        color=_SK_SUCCESS),
                        visible=avg > 0,
                    ),
                    ft.Text(vis_label, size=10, color=SK_TEXT_FAINT,
                            text_align=ft.TextAlign.CENTER, visible=bool(vis_label)),
                ],
            ),
        )

        criterion_cards = [
            _criterion_card(r.label, r.value, CRITERION_COLORS[i % len(CRITERION_COLORS)])
            for i, r in enumerate(results)
        ]

        return ft.ListView(
            controls=[avg_card, *criterion_cards], expand=True,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
        )

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify
    content.content = _build_body()

    return ft.View(
        route="/student/results",
        bgcolor=SK_BACKGROUND,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK,
                                 on_click=lambda _: page.go("/student/courses")),
            title=ft.Text("Mis resultados", color=SK_TEXT),
            bgcolor=SK_BACKGROUND, elevation=0,
        ),
        controls=[content],
    )
