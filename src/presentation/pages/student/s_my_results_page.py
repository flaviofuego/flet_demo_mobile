"""SMyResultsPage — student's evaluation results."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_BORDER, SK_TEXT, SK_TEXT_FAINT,
    SK_PRIMARY, CRITERION_COLORS,
)
from src.presentation.viewmodels.student_viewmodel import StudentViewModel


def s_my_results_page(page: ft.Page, vm: StudentViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _result_bar(label: str, value: float, color: str) -> ft.Container:
        fraction = max(0.0, min(1.0, (value - 2) / 3))
        return ft.Container(
            bgcolor=SK_SURFACE, border_radius=12,
            border=ft.Border.all(1, SK_BORDER),
            padding=14, margin=ft.margin.only(bottom=8),
            content=ft.Column(spacing=6, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(label, size=13, weight=ft.FontWeight.W_600, color=SK_TEXT),
                        ft.Text(
                            f"{value:.1f}" if value > 0 else "—",
                            size=13, weight=ft.FontWeight.W_700, color=color,
                        ),
                    ],
                ),
                ft.ProgressBar(value=fraction, bgcolor=f"{color}22", color=color, height=6),
            ]),
        )

    def _build_body() -> ft.Control:
        results = vm.my_results
        ev      = vm.active_eval
        avg     = vm.my_average
        badge   = vm.performance_badge
        vis_label = ""
        if ev:
            vis_label = "Resultados visibles" if ev.visibility == "public" else "Resultados privados"

        if not results or avg == 0:
            return ft.Container(expand=True, alignment=ft.Alignment(0, 0),
                               content=ft.Column(
                                   horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                   controls=[
                                       ft.Icon(ft.Icons.PENDING_OUTLINED, size=56, color=SK_TEXT_FAINT),
                                       ft.Text("Resultados pendientes", color=SK_TEXT_FAINT),
                                       ft.Text("Completa tu evaluación para ver resultados",
                                              size=12, color=SK_TEXT_FAINT,
                                              text_align=ft.TextAlign.CENTER),
                                   ]))

        avg_color = (
            "#059669" if avg >= 4.0
            else SK_PRIMARY if avg >= 3.0
            else "#F59E0B" if avg >= 2.5
            else "#EF4444"
        )

        header = ft.Container(
            bgcolor=SK_PRIMARY, border_radius=18, padding=20,
            margin=ft.margin.only(bottom=16),
            content=ft.Column(
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(badge, size=12, color="#EEEFFE", weight=ft.FontWeight.W_600),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(f"{avg:.2f}", size=48, weight=ft.FontWeight.W_900, color="#FFFFFF"),
                            ft.Text("/5.0", size=16, color="#EEEFFE"),
                        ],
                    ),
                    ft.Text(ev.name if ev else "", size=12, color="#EEEFFE",
                           text_align=ft.TextAlign.CENTER),
                    ft.Text(vis_label, size=10, color="#EEEFFE80",
                           text_align=ft.TextAlign.CENTER),
                ],
            ),
        )

        bars = [
            _result_bar(r.label, r.value, CRITERION_COLORS[i % len(CRITERION_COLORS)])
            for i, r in enumerate(results)
        ]

        return ft.ListView(
            controls=[header, *bars], expand=True,
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
