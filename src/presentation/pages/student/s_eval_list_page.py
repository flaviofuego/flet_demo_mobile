"""SEvalListPage — full evaluation history grouped by course."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_BORDER, SK_TEXT, SK_TEXT_FAINT, SK_PRIMARY,
)
from src.presentation.viewmodels.student_viewmodel import StudentViewModel, EvalStudentStatus


def s_eval_list_page(page: ft.Page, vm: StudentViewModel) -> ft.View:
    content = ft.Container(expand=True)

    STATUS_LABEL = {
        EvalStudentStatus.active_pending:   ("Pendiente",  "#7C83D6"),
        EvalStudentStatus.active_completed: ("Completada", "#059669"),
        EvalStudentStatus.closed_completed: ("Cerrada ✓",  "#6B7280"),
        EvalStudentStatus.closed_not_done:  ("Sin hacer",  "#EF4444"),
    }

    def _eval_row(ev) -> ft.Container:
        status = vm.eval_statuses.get(ev.id, EvalStudentStatus.active_pending)
        label, color = STATUS_LABEL.get(status, ("—", SK_TEXT_FAINT))

        def _evaluate(_) -> None:
            vm.select_eval_for_evaluation(ev)
            page.go("/student/peers")

        def _results(_) -> None:
            vm.select_eval_for_results(ev)
            page.go("/student/results")

        actions = []
        if ev.is_active and status == EvalStudentStatus.active_pending:
            actions.append(ft.TextButton("Evaluar", on_click=_evaluate))
        actions.append(ft.TextButton("Resultados", on_click=_results))

        return ft.Container(
            bgcolor=SK_SURFACE, border_radius=12,
            border=ft.Border.all(1, SK_BORDER),
            padding=14, margin=ft.margin.only(bottom=8),
            content=ft.Column(spacing=6, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(ev.name, size=14, weight=ft.FontWeight.W_600, color=SK_TEXT),
                        ft.Container(
                            bgcolor=f"#22{color[1:]}", border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            content=ft.Text(label, size=10, color=color, weight=ft.FontWeight.W_600),
                        ),
                    ],
                ),
                ft.Text(ev.course_name or ev.category_name, size=11, color=SK_TEXT_FAINT),
                ft.Row(spacing=6, controls=actions),
            ]),
        )

    def _build_body() -> ft.Control:
        evals = vm.evaluations
        if not evals:
            return ft.Container(expand=True, alignment=ft.Alignment(0, 0),
                               content=ft.Text("Sin evaluaciones", color=SK_TEXT_FAINT))
        groups: dict[str, list] = {}
        for ev in evals:
            groups.setdefault(ev.course_name or "Sin curso", []).append(ev)
        items: list[ft.Control] = []
        for course, evs in groups.items():
            items.append(ft.Container(
                padding=ft.padding.only(top=12, bottom=4),
                content=ft.Text(course.upper(), size=10, color=SK_TEXT_FAINT,
                               weight=ft.FontWeight.W_600),
            ))
            items.extend(_eval_row(ev) for ev in evs)
        return ft.ListView(controls=items, expand=True,
                          padding=ft.padding.symmetric(horizontal=16, vertical=8))

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify
    content.content = _build_body()

    return ft.View(
        route="/student/eval-list",
        bgcolor=SK_BACKGROUND,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK,
                                 on_click=lambda _: page.go("/student/courses")),
            title=ft.Text("Historial", color=SK_TEXT),
            bgcolor=SK_BACKGROUND, elevation=0,
        ),
        controls=[content],
    )
