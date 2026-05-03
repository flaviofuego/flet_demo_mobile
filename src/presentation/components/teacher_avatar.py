"""Gradient avatar for teacher pages."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import TK_GOLD, TK_BACKGROUND


def teacher_avatar(initials: str, size: int = 52) -> ft.Container:
    radius = round(size * 0.31)
    font_size = round(size * 0.35)
    return ft.Container(
        width=size, height=size,
        border_radius=radius,
        gradient=ft.LinearGradient(
            colors=[TK_GOLD, "#E3C26E"],
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
        ),
        alignment=ft.Alignment(0, 0),
        content=ft.Text(
            initials[:2].upper() if initials else "?",
            size=font_size,
            weight=ft.FontWeight.W_700,
            color=TK_BACKGROUND,
        ),
    )
