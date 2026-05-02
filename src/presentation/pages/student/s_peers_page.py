"""SPeersPage — list of peers to evaluate."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_BORDER, SK_TEXT, SK_TEXT_FAINT,
    SK_PRIMARY, SK_PRIMARY_LIGHT,
)
from src.presentation.components.avatar_circle import avatar_circle
from src.presentation.viewmodels.student_viewmodel import StudentViewModel


def s_peers_page(page: ft.Page, vm: StudentViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _peer_tile(peer) -> ft.Container:
        done = peer.evaluated
        status_icon  = ft.Icons.CHECK_CIRCLE if done else ft.Icons.RADIO_BUTTON_UNCHECKED
        status_color = "#059669" if done else SK_TEXT_FAINT

        def _on_tap(_) -> None:
            if not done:
                vm.select_peer(peer)
                page.go("/student/peer-score")

        return ft.Container(
            bgcolor=SK_SURFACE, border_radius=14,
            border=ft.border.all(1, SK_BORDER),
            padding=14, margin=ft.margin.only(bottom=8),
            on_click=_on_tap,
            content=ft.Row(spacing=12, controls=[
                avatar_circle(peer.initials, bg_color=SK_PRIMARY),
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text(peer.name, size=14, weight=ft.FontWeight.W_500, color=SK_TEXT),
                    ft.Text(
                        "Evaluado ✓" if done else "Pendiente de evaluar",
                        size=11, color=status_color,
                    ),
                ]),
                ft.Icon(status_icon, color=status_color, size=20),
            ]),
        )

    def _build_body() -> ft.Control:
        ev    = vm.active_eval
        peers = vm.peers
        if not peers:
            return ft.Container(expand=True, alignment=ft.alignment.center,
                               content=ft.Column(
                                   horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                   controls=[
                                       ft.Icon(ft.Icons.GROUP_OUTLINED, size=56, color=SK_TEXT_FAINT),
                                       ft.Text("Sin compañeros en esta evaluación", color=SK_TEXT_FAINT),
                                   ]))

        submit_btn = ft.ElevatedButton(
            f"Enviar evaluación ({vm.done_count}/{vm.total_peers})",
            disabled=not vm.all_evaluated,
            style=ft.ButtonStyle(bgcolor=SK_PRIMARY, color="#FFFFFF"),
            on_click=_on_submit,
            expand=True,
        )

        return ft.Column(expand=True, controls=[
            ft.Container(
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                content=ft.Column(spacing=4, controls=[
                    ft.Text(ev.name if ev else "", size=16, weight=ft.FontWeight.W_700, color=SK_TEXT),
                    ft.Text(vm.current_group_name, size=12, color=SK_TEXT_FAINT),
                    ft.ProgressBar(value=vm.eval_progress, bgcolor=SK_PRIMARY_LIGHT, color=SK_PRIMARY),
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
        def _do() -> None:
            vm.submit_evaluation()
            page.go("/student/courses")
        page.run_thread(_do)

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
