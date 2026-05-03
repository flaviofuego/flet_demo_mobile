"""SPeerScorePage — score a peer on 4 criteria (2-5 scale)."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_SURFACE_ALT, SK_BORDER,
    SK_TEXT, SK_TEXT_FAINT, SK_PRIMARY,
    CRITERION_COLORS,
)
from src.presentation.components.avatar_circle import avatar_circle
from src.presentation.viewmodels.student_viewmodel import StudentViewModel
from src.domain.models.peer_evaluation import EvalCriterion


SCORE_LABELS = {2: "Insuficiente", 3: "Aceptable", 4: "Bueno", 5: "Excelente"}


def s_peer_score_page(page: ft.Page, vm: StudentViewModel) -> ft.View:
    content = ft.Container(expand=True)

    save_btn_label = ft.Text(
        "Guardar evaluación", size=15, weight=ft.FontWeight.W_700,
        color="#FFFFFF", text_align=ft.TextAlign.CENTER,
    )
    save_btn_box = ft.Container(
        expand=True,
        bgcolor=f"#55{SK_PRIMARY[1:]}",
        border_radius=14,
        padding=ft.padding.symmetric(vertical=14),
        alignment=ft.Alignment(0, 0),
        content=save_btn_label,
    )
    save_btn = ft.GestureDetector(
        on_tap=(lambda _: None),
        content=save_btn_box,
    )

    def _on_save(_) -> None:
        vm.save_peer_score()
        page.go("/student/peers")

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    def _criterion_row(criterion: EvalCriterion, color: str) -> ft.Container:
        current = vm.scores.get(criterion.id, 0)

        def _set(val: int) -> None:
            vm.set_score(criterion.id, val)
            _notify()

        score_btns = ft.Row(
            spacing=5,
            controls=[
                ft.GestureDetector(
                    on_tap=lambda _, v=v: _set(v),
                    content=ft.Container(
                        expand=True,
                        bgcolor=color if current == v else SK_SURFACE,
                        border_radius=9,
                        border=ft.Border.all(
                            1, color if current == v else SK_BORDER),
                        padding=ft.padding.symmetric(vertical=9),
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            str(v), size=13,
                            weight=ft.FontWeight.W_700,
                            color="#FFFFFF" if current == v else SK_TEXT_FAINT,
                        ),
                    ),
                )
                for v in range(2, 6)
            ],
        )

        level_desc = SCORE_LABELS.get(current, "") if current else ""

        return ft.Container(
            bgcolor=SK_SURFACE_ALT, border_radius=14,
            padding=14, margin=ft.margin.only(bottom=10),
            content=ft.Column(spacing=10, controls=[
                ft.Row(spacing=8, controls=[
                    ft.Container(width=8, height=8, border_radius=4, bgcolor=color),
                    ft.Text(criterion.label, size=13, weight=ft.FontWeight.W_700,
                            color=SK_TEXT, expand=True),
                    ft.Container(
                        bgcolor=f"#22{color[1:]}", border_radius=8,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        visible=current is not None and current > 0,
                        content=ft.Text(
                            str(current) if current else "",
                            size=12, weight=ft.FontWeight.W_800, color=color,
                        ),
                    ),
                ]),
                score_btns,
                ft.Text(level_desc, size=10, color=SK_TEXT_FAINT,
                        visible=bool(level_desc)),
            ]),
        )

    def _build_body() -> ft.Control:
        peer = vm.current_peer
        if peer is None:
            return ft.Container(
                expand=True, alignment=ft.Alignment(0, 0),
                content=ft.Text("Selecciona un compañero primero",
                               color=SK_TEXT_FAINT))

        disabled = not vm.all_criteria_scored
        save_btn.on_tap      = (lambda _: None) if disabled else _on_save
        save_btn_box.bgcolor = f"#55{SK_PRIMARY[1:]}" if disabled else SK_PRIMARY

        criterion_rows = [
            _criterion_row(c, CRITERION_COLORS[i])
            for i, c in enumerate(EvalCriterion.DEFAULTS)
        ]

        return ft.Column(expand=True, controls=[
            ft.Container(
                padding=16,
                content=ft.Row(spacing=12, controls=[
                    avatar_circle(peer.initials, size=52, bg_color=SK_PRIMARY),
                    ft.Column(expand=True, spacing=2, controls=[
                        ft.Text(peer.name, size=16, weight=ft.FontWeight.W_700,
                               color=SK_TEXT),
                        ft.Text(vm.active_eval.name if vm.active_eval else "",
                               size=12, color=SK_TEXT_FAINT),
                    ]),
                ]),
            ),
            ft.ListView(
                controls=criterion_rows, expand=True,
                padding=ft.padding.symmetric(horizontal=16),
            ),
            ft.Container(padding=16, content=save_btn),
        ])

    vm._notify = _notify
    content.content = _build_body()

    return ft.View(
        route="/student/peer-score",
        bgcolor=SK_BACKGROUND,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK,
                                 on_click=lambda _: page.go("/student/peers")),
            title=ft.Text("Evaluar compañero", color=SK_TEXT),
            bgcolor=SK_BACKGROUND, elevation=0,
        ),
        controls=[content],
    )
