"""SPeersPage — list of peers to evaluate."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_BORDER, SK_TEXT, SK_TEXT_FAINT,
    SK_PRIMARY, SK_PRIMARY_MID, SK_PRIMARY_LIGHT, SK_SURFACE_ALT,
)
from src.presentation.components.avatar_circle import avatar_circle
from src.presentation.viewmodels.student_viewmodel import StudentViewModel


def s_peers_page(page: ft.Page, vm: StudentViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _peer_tile(peer) -> ft.Container:
        done = peer.evaluated

        def _on_tap(_) -> None:
            if not done:
                vm.select_peer(peer)
                page.go("/student/peer-score")

        return ft.Container(
            bgcolor=SK_PRIMARY_LIGHT if done else SK_SURFACE,
            border_radius=14,
            border=ft.Border.all(1, SK_PRIMARY_MID if done else SK_BORDER),
            padding=14, margin=ft.margin.only(bottom=8),
            on_click=_on_tap,
            content=ft.Row(spacing=12, controls=[
                avatar_circle(peer.initials,
                              bg_color=SK_PRIMARY if done else SK_SURFACE_ALT),
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text(peer.name, size=14, weight=ft.FontWeight.W_500,
                            color=SK_TEXT),
                    ft.Text(
                        "Evaluado ✓" if done else "Pendiente de evaluar",
                        size=11,
                        color=SK_PRIMARY if done else SK_TEXT_FAINT,
                    ),
                ]),
                ft.Icon(ft.Icons.CHECK_CIRCLE if done else ft.Icons.CHEVRON_RIGHT,
                        color=SK_PRIMARY if done else SK_TEXT_FAINT, size=20),
            ]),
        )

    def _build_body() -> ft.Control:
        ev    = vm.active_eval
        peers = vm.peers
        if not peers:
            return ft.Container(expand=True, alignment=ft.Alignment(0, 0),
                               content=ft.Column(
                                   horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                   controls=[
                                       ft.Icon(ft.Icons.GROUP_OUTLINED, size=56,
                                               color=SK_TEXT_FAINT),
                                       ft.Text("Sin compañeros en esta evaluación",
                                               color=SK_TEXT_FAINT),
                                   ]))

        disabled = not vm.all_evaluated
        submit_btn = ft.GestureDetector(
            on_tap=(lambda _: None) if disabled else _on_submit,
            content=ft.Container(
                expand=True,
                bgcolor=f"{SK_PRIMARY}66" if disabled else SK_PRIMARY,
                border_radius=14,
                padding=ft.padding.symmetric(vertical=14),
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    f"Enviar evaluación ({vm.done_count}/{vm.total_peers})",
                    size=15, weight=ft.FontWeight.W_700,
                    color="#FFFFFF", text_align=ft.TextAlign.CENTER,
                ),
            ),
        )

        return ft.Column(expand=True, controls=[
            ft.Container(
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                content=ft.Column(spacing=4, controls=[
                    ft.Text(ev.name if ev else "", size=16,
                            weight=ft.FontWeight.W_700, color=SK_TEXT),
                    ft.Text(vm.current_group_name, size=12, color=SK_TEXT_FAINT),
                    ft.ProgressBar(value=vm.eval_progress,
                                   bgcolor=SK_PRIMARY_LIGHT, color=SK_PRIMARY),
                ]),
            ),
            ft.ListView(
                controls=[_peer_tile(p) for p in peers],
                expand=True,
                padding=ft.padding.symmetric(horizontal=16),
            ),
            ft.Container(padding=16, content=submit_btn),
        ])

    def _on_submit(_) -> None:
        async def _do() -> None:
            vm.submit_evaluation()
            await page.push_route("/student/courses")
        page.run_task(_do)

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify
    content.content = _build_body()

    return ft.View(
        route="/student/peers",
        bgcolor=SK_BACKGROUND,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK,
                                 on_click=lambda _: page.go("/student/courses")),
            title=ft.Text("Compañeros", color=SK_TEXT),
            bgcolor=SK_BACKGROUND, elevation=0,
        ),
        controls=[content],
    )
