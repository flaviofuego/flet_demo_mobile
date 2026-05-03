"""SPeerScorePage — score a peer on 4 criteria (2-5 scale)."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_BORDER, SK_TEXT, SK_TEXT_FAINT, SK_PRIMARY,
    CRITERION_COLORS,
)
from src.presentation.components.avatar_circle import avatar_circle
from src.presentation.viewmodels.student_viewmodel import StudentViewModel
from src.domain.models.peer_evaluation import EvalCriterion


def s_peer_score_page(page: ft.Page, vm: StudentViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _criterion_row(criterion: EvalCriterion, color: str) -> ft.Container:
        current_score = vm.scores.get(criterion.id, 0)
        level_text = ft.Text(
            EvalCriterion.level_for(current_score) if current_score >= 2 else "Sin puntuar",
            size=11, color=color,
        )
        slider = ft.Slider(
            min=2, max=5, divisions=3,
            value=float(current_score) if current_score >= 2 else 2.0,
            active_color=color, thumb_color=color,
        )

        def _on_change(e) -> None:
            val = int(round(e.control.value))
            vm.set_score(criterion.id, val)
            level_text.value = EvalCriterion.level_for(val)
            # update save button state
            save_btn.disabled = not vm.all_criteria_scored
            page.update()

        slider.on_change = _on_change

        return ft.Container(
            bgcolor=SK_SURFACE, border_radius=14,
            border=ft.Border.all(1, SK_BORDER),
            padding=16, margin=ft.margin.only(bottom=10),
            content=ft.Column(spacing=6, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(spacing=8, controls=[
                            ft.Container(width=8, height=8, bgcolor=color, border_radius=4),
                            ft.Text(criterion.label, size=13, weight=ft.FontWeight.W_600, color=SK_TEXT),
                        ]),
                        level_text,
                    ],
                ),
                slider,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Necesita Mejorar", size=9, color=SK_TEXT_FAINT),
                        ft.Text("Excelente", size=9, color=SK_TEXT_FAINT),
                    ],
                ),
            ]),
        )

    _save_disabled = [not vm.all_criteria_scored]
    save_btn_label = ft.Text(
        "Guardar evaluación", size=15, weight=ft.FontWeight.W_700,
        color="#FFFFFF", text_align=ft.TextAlign.CENTER,
    )
    save_btn_box = ft.Container(
        expand=True,
        bgcolor=f"{SK_PRIMARY}55" if _save_disabled[0] else SK_PRIMARY,
        border_radius=30,
        padding=ft.padding.symmetric(vertical=14),
        alignment=ft.Alignment(0, 0),
        content=save_btn_label,
    )
    save_btn = ft.GestureDetector(content=save_btn_box)

    def _on_save(_) -> None:
        vm.save_peer_score()
        page.go("/student/peers")

    save_btn.on_tap = None if _save_disabled[0] else _on_save

    def _build_body() -> ft.Control:
        peer = vm.current_peer
        if peer is None:
            return ft.Container(expand=True, alignment=ft.Alignment(0, 0),
                               content=ft.Text("Selecciona un compañero primero", color=SK_TEXT_FAINT))

        disabled = not vm.all_criteria_scored
        save_btn.on_tap      = None if disabled else _on_save
        save_btn_box.bgcolor = f"{SK_PRIMARY}55" if disabled else SK_PRIMARY

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
                        ft.Text(peer.name, size=16, weight=ft.FontWeight.W_700, color=SK_TEXT),
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

    def _notify() -> None:
        content.content = _build_body()
        page.update()

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
