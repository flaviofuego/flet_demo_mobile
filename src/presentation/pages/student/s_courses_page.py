"""SCoursesPage — student's main screen showing their evaluations."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_SURFACE_ALT, SK_BORDER,
    SK_TEXT, SK_TEXT_FAINT, SK_PRIMARY, SK_PRIMARY_LIGHT,
)
from src.presentation.components.avatar_circle import avatar_circle
from src.presentation.viewmodels.student_viewmodel import StudentViewModel, EvalStudentStatus


def s_courses_page(page: ft.Page, vm: StudentViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _badge(status: EvalStudentStatus) -> ft.Container:
        cfg = {
            EvalStudentStatus.active_pending:   (SK_PRIMARY,    SK_PRIMARY_LIGHT, "ACTIVA"),
            EvalStudentStatus.active_completed: ("#059669",     "#D1FAE5",        "COMPLETADA"),
            EvalStudentStatus.closed_completed: (SK_TEXT_FAINT, SK_SURFACE_ALT,   "CERRADA"),
            EvalStudentStatus.closed_not_done:  ("#EF4444",     "#FEF2F2",        "PERDIDA"),
        }.get(status, (SK_TEXT_FAINT, SK_SURFACE_ALT, "—"))
        text_color, bg_color, label = cfg
        return ft.Container(
            bgcolor=bg_color, border_radius=6,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            content=ft.Text(label, size=10, weight=ft.FontWeight.W_700,
                            color=text_color),
        )

    def _eval_card(ev) -> ft.Container:
        status = vm.eval_statuses.get(ev.id, EvalStudentStatus.active_pending)

        def _evaluate(_) -> None:
            vm.select_eval_for_evaluation(ev)
            page.go("/student/peers")

        def _results(_) -> None:
            vm.select_eval_for_results(ev)
            page.go("/student/results")

        actions = []
        if ev.is_active and status == EvalStudentStatus.active_pending:
            actions.append(ft.GestureDetector(
                on_tap=_evaluate,
                content=ft.Container(
                    bgcolor=SK_PRIMARY, border_radius=14,
                    padding=ft.padding.symmetric(horizontal=14, vertical=8),
                    content=ft.Text("Evaluar", size=13, weight=ft.FontWeight.W_700,
                                    color="#FFFFFF"),
                ),
            ))
        actions.append(ft.OutlinedButton("Resultados", on_click=_results))

        return ft.Container(
            bgcolor=SK_SURFACE, border_radius=14,
            border=ft.Border.all(1, SK_BORDER),
            padding=16, margin=ft.margin.only(bottom=10),
            content=ft.Column(spacing=8, controls=[
                ft.Row(controls=[
                    ft.Column(expand=True, spacing=2, controls=[
                        ft.Text(ev.name, size=14, weight=ft.FontWeight.W_600,
                                color=SK_TEXT),
                        ft.Text(ev.course_name or ev.category_name,
                                size=11, color=SK_TEXT_FAINT),
                    ]),
                    _badge(status),
                ]),
                ft.Row(spacing=8, controls=actions),
            ]),
        )

    def _hero_card() -> ft.Control:
        ev = vm.active_eval
        if ev is None or not ev.is_active:
            return ft.Container(height=0)
        status = vm.eval_statuses.get(ev.id, EvalStudentStatus.active_pending)

        def _on_evaluate(_) -> None:
            vm.select_eval_for_evaluation(ev)
            page.go("/student/peers")

        return ft.Container(
            bgcolor=SK_PRIMARY, border_radius=18, padding=20,
            margin=ft.margin.only(bottom=16),
            content=ft.Column(spacing=6, controls=[
                ft.Text("Evaluación activa", size=11, color="#EEEFFE",
                        weight=ft.FontWeight.W_600),
                ft.Text(ev.name, size=18, weight=ft.FontWeight.W_800, color="#FFFFFF"),
                ft.Text(ev.category_name, size=12, color="#EEEFFE"),
                ft.Container(height=4),
                ft.ProgressBar(value=vm.eval_progress, bgcolor="#EEEFFE",
                               color="#FFFFFF"),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(f"{vm.done_count}/{vm.total_peers} evaluados",
                                size=11, color="#EEEFFE"),
                        ft.GestureDetector(
                            on_tap=(lambda _: None)
                            if status == EvalStudentStatus.active_completed
                            else _on_evaluate,
                            content=ft.Container(
                                bgcolor="#FFFFFF",
                                border_radius=14,
                                padding=ft.padding.symmetric(horizontal=14, vertical=8),
                                content=ft.Text(
                                    "Completada"
                                    if status == EvalStudentStatus.active_completed
                                    else "Evaluar ahora",
                                    size=13, weight=ft.FontWeight.W_700,
                                    color=SK_PRIMARY,
                                ),
                            ),
                        ),
                    ],
                ),
            ]),
        )

    def _profile_sheet() -> ft.BottomSheet:
        s = vm.student
        initials = s.initials if s else "?"
        name = s.name if s else ""
        email = s.email if s else ""

        async def _logout(_) -> None:
            page.pop_dialog()
            vm.logout()
            await page.push_route("/login")

        bs = ft.BottomSheet(
            open=True,
            content=ft.Container(
                padding=24,
                bgcolor=SK_SURFACE,
                border_radius=ft.border_radius.only(top_left=20, top_right=20),
                content=ft.Column(tight=True, controls=[
                    ft.Row(spacing=12, controls=[
                        avatar_circle(initials, size=48, bg_color=SK_PRIMARY),
                        ft.Column(spacing=2, controls=[
                            ft.Text(name, size=16, weight=ft.FontWeight.W_600,
                                    color=SK_TEXT),
                            ft.Text(email, size=12, color=SK_TEXT_FAINT),
                        ]),
                    ]),
                    ft.Divider(color=SK_BORDER),
                    ft.GestureDetector(
                        on_tap=_logout,
                        content=ft.Container(
                            expand=True,
                            bgcolor="#1AEF4444",
                            border_radius=14,
                            border=ft.Border.all(1, "#99EF4444"),
                            padding=ft.padding.symmetric(vertical=14),
                            alignment=ft.Alignment(0, 0),
                            content=ft.Row(
                                spacing=8,
                                alignment=ft.MainAxisAlignment.CENTER,
                                tight=True,
                                controls=[
                                    ft.Icon(ft.Icons.LOGOUT_ROUNDED,
                                            size=16, color="#EF4444"),
                                    ft.Text("Cerrar sesión", size=14,
                                            weight=ft.FontWeight.W_700,
                                            color="#EF4444"),
                                ],
                            ),
                        ),
                    ),
                ]),
            ),
        )
        return bs

    def _build_body() -> ft.Control:
        if vm.is_loading:
            return ft.Container(expand=True, alignment=ft.Alignment(0, 0),
                               content=ft.ProgressRing(color=SK_PRIMARY))
        evals = vm.evaluations
        if not evals:
            return ft.Container(expand=True, alignment=ft.Alignment(0, 0),
                               content=ft.Column(
                                   horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                   controls=[
                                       ft.Icon(ft.Icons.INBOX_OUTLINED, size=56,
                                               color=SK_TEXT_FAINT),
                                       ft.Text("Sin evaluaciones", color=SK_TEXT_FAINT,
                                               size=14),
                                   ]))
        active = [e for e in evals if e.is_active]
        closed = [e for e in evals if not e.is_active]
        items: list[ft.Control] = [_hero_card()]
        if active:
            items.append(ft.Text("ACTIVAS", size=10, weight=ft.FontWeight.W_600,
                                color=SK_TEXT_FAINT))
            items.extend(_eval_card(e) for e in active)
        if closed:
            items.append(ft.Text("CERRADAS", size=10, weight=ft.FontWeight.W_600,
                                color=SK_TEXT_FAINT))
            items.extend(_eval_card(e) for e in closed)
        return ft.ListView(controls=items, expand=True,
                          padding=ft.padding.symmetric(horizontal=16, vertical=8))

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify

    if not vm.is_logged_in:
        page.run_thread(vm.check_session)
    else:
        content.content = _build_body()

    return ft.View(
        route="/student/courses",
        bgcolor=SK_BACKGROUND,
        appbar=ft.AppBar(
            title=ft.Text("Mis evaluaciones", color=SK_TEXT),
            bgcolor=SK_BACKGROUND, elevation=0,
            actions=[
                ft.IconButton(ft.Icons.HISTORY, tooltip="Historial",
                             on_click=lambda _: page.go("/student/eval-list")),
                ft.IconButton(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, tooltip="Perfil",
                             on_click=lambda _: page.show_dialog(_profile_sheet())),
            ],
        ),
        controls=[content],
    )
