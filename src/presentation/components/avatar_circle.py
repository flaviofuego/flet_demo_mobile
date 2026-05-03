"""Reusable circular avatar component showing initials."""
from __future__ import annotations
import flet as ft


def avatar_circle(
    initials: str,
    size: int = 40,
    bg_color: str = "#7C83D6",
    text_color: str = "#FFFFFF",
    font_size: int = 14,
) -> ft.Container:
    return ft.Container(
        width=size,
        height=size,
        bgcolor=bg_color,
        border_radius=size // 2,
        alignment=ft.Alignment(0, 0),
        content=ft.Text(
            initials[:2].upper(),
            size=font_size,
            weight=ft.FontWeight.BOLD,
            color=text_color,
        ),
    )
