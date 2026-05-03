"""Login page — unified auth (teacher first, then student)."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_BORDER, SK_TEXT, SK_TEXT_FAINT,
    SK_PRIMARY, SK_PRIMARY_LIGHT,
    TK_BACKGROUND, TK_SURFACE, TK_BORDER as TK_BORDER_,
    TK_TEXT as TK_TEXT_, TK_TEXT_FAINT as TK_TEXT_FAINT_, TK_GOLD,
)
from src.presentation.viewmodels.login_viewmodel import LoginViewModel
from src.presentation.viewmodels.student_viewmodel import StudentViewModel
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def login_page(
    page: ft.Page,
    login_vm: LoginViewModel,
    student_vm: StudentViewModel,
    teacher_vm: TeacherViewModel,
) -> ft.View:
    is_dark = [page.theme_mode != ft.ThemeMode.LIGHT]

    def _bg()      -> str: return TK_BACKGROUND  if is_dark[0] else SK_BACKGROUND
    def _surf()    -> str: return TK_SURFACE      if is_dark[0] else SK_SURFACE
    def _border()  -> str: return TK_BORDER_      if is_dark[0] else SK_BORDER
    def _text()    -> str: return TK_TEXT_        if is_dark[0] else SK_TEXT
    def _faint()   -> str: return TK_TEXT_FAINT_  if is_dark[0] else SK_TEXT_FAINT
    def _accent()  -> str: return TK_GOLD         if is_dark[0] else SK_PRIMARY
    def _icon_bg() -> str: return f"#33{TK_GOLD[1:]}"  if is_dark[0] else SK_PRIMARY_LIGHT

    email_field = ft.TextField(
        hint_text="Correo institucional",
        prefix_icon=ft.Icons.MAIL_OUTLINE_ROUNDED,
        focused_border_color=_accent(),
        border_color=_border(),
        bgcolor=_surf(),
        border_radius=12,
    )
    password_field = ft.TextField(
        hint_text="Contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED,
        focused_border_color=_accent(),
        border_color=_border(),
        bgcolor=_surf(),
        border_radius=12,
    )
    error_text = ft.Text("", color="#EF4444", size=12, visible=False)

    login_label = ft.Text(
        "Iniciar sesión", size=15, weight=ft.FontWeight.W_700,
        color=TK_BACKGROUND, text_align=ft.TextAlign.CENTER,
    )
    login_box = ft.Container(
        expand=True, bgcolor=_accent(), border_radius=14,
        padding=ft.padding.symmetric(vertical=14),
        alignment=ft.Alignment(0, 0),
        content=login_label,
    )
    login_btn = ft.GestureDetector(content=login_box)

    register_label = ft.Text(
        "Crear cuenta", size=15, weight=ft.FontWeight.W_700,
        color=_text(), text_align=ft.TextAlign.CENTER,
    )
    register_box = ft.Container(
        expand=True, bgcolor=ft.Colors.TRANSPARENT, border_radius=14,
        border=ft.Border.all(1, _border()),
        padding=ft.padding.symmetric(vertical=14),
        alignment=ft.Alignment(0, 0),
        content=register_label,
    )
    register_btn = ft.GestureDetector(content=register_box)

    theme_btn = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE_ROUNDED if is_dark[0] else ft.Icons.DARK_MODE_ROUNDED,
        icon_color=_faint(),
    )
    icon_box = ft.Container(
        width=44, height=44, border_radius=12,
        bgcolor=_icon_bg(),
        alignment=ft.Alignment(0, 0),
        content=ft.Icon(ft.Icons.SCHOOL_ROUNDED, color=_accent(), size=24),
    )
    title_text      = ft.Text("Bienvenido a EvalUn", size=26, weight=ft.FontWeight.W_800, color=_text())
    no_account_text = ft.Text("¿No tienes cuenta?", size=12, color=_faint(), text_align=ft.TextAlign.CENTER)
    sso_text        = ft.Text("Autenticado por Roble SSO", size=11, color=_faint(), text_align=ft.TextAlign.CENTER)
    card = ft.Container(
        expand=True, bgcolor=_surf(), border_radius=20,
        border=ft.Border.all(1, _border()), padding=24,
    )

    def _notify() -> None:
        error_text.value   = login_vm.auth_error
        error_text.visible = bool(login_vm.auth_error)
        loading = login_vm.is_loading
        login_btn.on_tap       = (lambda _: None) if loading else _on_login
        login_box.bgcolor      = f"{_accent()}66" if loading else _accent()
        login_label.value      = "Cargando..." if loading else "Iniciar sesión"
        page.update()

    login_vm._notify = _notify

    def _on_login(_) -> None:
        async def _do() -> None:
            result = login_vm.login(email_field.value or "", password_field.value or "")
            if result is None:
                return
            if result.role.value == "teacher":
                teacher_vm.check_session()
                student_vm.student = None
            else:
                student_vm.check_session()
                teacher_vm.teacher = None
            await page.push_route(result.home_route)
        page.run_task(_do)

    def _on_register(_) -> None:
        login_vm.clear_error()
        page.go("/register")

    def _toggle_theme(_) -> None:
        is_dark[0] = not is_dark[0]
        page.theme_mode = ft.ThemeMode.DARK if is_dark[0] else ft.ThemeMode.LIGHT
        theme_btn.icon       = ft.Icons.LIGHT_MODE_ROUNDED if is_dark[0] else ft.Icons.DARK_MODE_ROUNDED
        theme_btn.icon_color = _faint()
        email_field.focused_border_color    = _accent()
        email_field.border_color            = _border()
        email_field.bgcolor                 = _surf()
        password_field.focused_border_color = _accent()
        password_field.border_color         = _border()
        password_field.bgcolor              = _surf()
        login_box.bgcolor                   = _accent()
        login_label.color                   = TK_BACKGROUND
        register_box.border                 = ft.Border.all(1, _border())
        register_label.color                = _text()
        icon_box.bgcolor                    = _icon_bg()
        icon_box.content.color              = _accent()
        card.bgcolor                        = _surf()
        card.border                         = ft.Border.all(1, _border())
        title_text.color                    = _text()
        no_account_text.color               = _faint()
        sso_text.color                      = _faint()
        view.bgcolor                        = _bg()
        page.update()

    login_btn.on_tap    = _on_login
    register_btn.on_tap = _on_register
    theme_btn.on_click  = _toggle_theme

    card.content = ft.Column(
        scroll=ft.ScrollMode.AUTO, expand=True, spacing=12,
        controls=[
            ft.Row(controls=[icon_box, ft.Container(expand=True), theme_btn]),
            title_text,
            ft.Container(height=2),
            email_field,
            password_field,
            error_text,
            login_btn,
            no_account_text,
            register_btn,
            ft.Container(height=4),
            sso_text,
        ],
    )

    view = ft.View(
        route="/login",
        bgcolor=_bg(),
        padding=24,
        controls=[ft.SafeArea(expand=True, content=card)],
    )
    return view
