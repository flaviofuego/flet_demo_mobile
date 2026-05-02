"""HomePage – the main screen of the application.

Pages compose Flet controls and delegate all state logic to their
:class:`~src.presentation.viewmodels.home_viewmodel.HomeViewModel`.
They contain *only* presentation logic (what to show given the current state).
"""

from __future__ import annotations

import flet as ft

from src.presentation.components.user_card import user_card
from src.presentation.viewmodels.home_viewmodel import HomeViewModel


def home_page(page: ft.Page, view_model: HomeViewModel) -> ft.View:
    """Build and return the home :class:`flet.View`.

    This function follows the functional-page pattern: it creates the full
    view tree once, wires up event handlers, and returns the view so that
    the router can push it onto the navigation stack.

    Args:
        page:       The root :class:`flet.Page` (used for updates).
        view_model: The :class:`HomeViewModel` that owns the page's state.

    Returns:
        A fully configured :class:`flet.View`.
    """
    # ------------------------------------------------------------------ #
    # State-derived helpers                                               #
    # ------------------------------------------------------------------ #

    def _build_body() -> ft.Control:
        if view_model.is_loading:
            return ft.Column(
                controls=[ft.ProgressRing()],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            )

        if view_model.error_message:
            return ft.Column(
                controls=[
                    ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED, size=48),
                    ft.Text(
                        view_model.error_message,
                        color=ft.Colors.RED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.ElevatedButton("Retry", on_click=lambda _: _refresh()),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
                expand=True,
            )

        if not view_model.users:
            return ft.Column(
                controls=[
                    ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=64, color=ft.Colors.GREY_400),
                    ft.Text("No users found", color=ft.Colors.GREY_500),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            )

        return ft.ListView(
            controls=[user_card(u) for u in view_model.users],
            expand=True,
            padding=ft.padding.symmetric(vertical=8),
        )

    # ------------------------------------------------------------------ #
    # Mutable content container                                           #
    # ------------------------------------------------------------------ #

    content = ft.Container(content=_build_body(), expand=True)

    def _notify() -> None:
        """Rebuild the page body whenever the view model changes."""
        content.content = _build_body()
        page.update()

    view_model._notify = _notify  # wire the notifier after creation

    # ------------------------------------------------------------------ #
    # Actions                                                             #
    # ------------------------------------------------------------------ #

    def _refresh() -> None:
        view_model.load_users()

    # Trigger initial load
    view_model.load_users()

    # ------------------------------------------------------------------ #
    # Assemble the view                                                   #
    # ------------------------------------------------------------------ #

    return ft.View(
        route="/",
        controls=[
            ft.AppBar(
                title=ft.Text("Users"),
                center_title=True,
                bgcolor=ft.Colors.BLUE_700,
                color=ft.Colors.WHITE,
                actions=[
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        on_click=lambda _: _refresh(),
                        tooltip="Refresh",
                    )
                ],
            ),
            content,
        ],
        bgcolor=ft.Colors.GREY_100,
    )
