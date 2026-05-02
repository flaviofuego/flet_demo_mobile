"""UserCard – a reusable Flet component that renders one user.

Reusable components live in the *components* package and are imported by
pages.  They receive only the data they need to display, keeping them
decoupled from any specific page or view model.
"""

from __future__ import annotations

import flet as ft

from src.domain.entities.user import User


def user_card(user: User) -> ft.Card:
    """Return a :class:`flet.Card` control that displays *user* information.

    Args:
        user: The domain entity whose data will be displayed.

    Returns:
        A ``flet.Card`` ready to be added to any Flet control tree.
    """
    return ft.Card(
        content=ft.Container(
            content=ft.Row(
                controls=[
                    ft.CircleAvatar(
                        content=ft.Text(
                            user.display_name()[0],
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        radius=24,
                        bgcolor=ft.Colors.BLUE_200,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                user.display_name(),
                                weight=ft.FontWeight.W_600,
                                size=16,
                            ),
                            ft.Text(
                                user.email,
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(16),
        ),
        elevation=2,
        margin=ft.margin.symmetric(vertical=4, horizontal=8),
    )
