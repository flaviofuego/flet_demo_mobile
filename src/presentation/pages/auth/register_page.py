"""Register page — student or teacher registration."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_SURFACE_ALT, SK_BORDER,
    SK_TEXT, SK_TEXT_FAINT, SK_PRIMARY, SK_PRIMARY_LIGHT,
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT as TK_SURFACE_ALT_,
    TK_BORDER as TK_BORDER_, TK_TEXT as TK_TEXT_,
    TK_TEXT_FAINT as TK_TEXT_FAINT_, TK_GOLD,
)
from src.presentation.viewmodels.student_viewmodel import StudentViewModel
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def register_page(
    page: ft.Page,
    student_vm: StudentViewModel,
    teacher_vm: TeacherViewModel,
) -> ft.View:
    is_dark   = [page.theme_mode != ft.ThemeMode.LIGHT]
    sel_tab   = [0]  # 0=Estudiante, 1=Profesor

    def _bg()       -> str: return TK_BACKGROUND   if is_dark[0] else SK_BACKGROUND
    def _surf()     -> str: return TK_SURFACE       if is_dark[0] else SK_SURFACE
    def _surf_alt() -> str: return TK_SURFACE_ALT_  if is_dark[0] else SK_SURFACE_ALT
    def _border()   -> str: return TK_BORDER_       if is_dark[0] else SK_BORDER
    def _text()     -> str: return TK_TEXT_         if is_dark[0] else SK_TEXT
    def _faint()    -> str: return TK_TEXT_FAINT_   if is_dark[0] else SK_TEXT_FAINT
    def _accent()   -> str: return TK_GOLD          if is_dark[0] else SK_PRIMARY
    def _icon_bg()  -> str: return f"{TK_GOLD}22"   if is_dark[0] else SK_PRIMARY_LIGHT

    def _tf_style(hint: str, icon, password=False) -> ft.TextField:
        return ft.TextField(
            hint_text=hint,
            prefix_icon=icon,
            password=password,
            can_reveal_password=password,
            focused_border_color=_accent(),
            border_color=_border(),
            bgcolor=_surf(),
            border_radius=12,
        )

    name_field    = _tf_style("Nombre completo",       ft.Icons.PERSON_OUTLINE_ROUNDED)
    email_field   = _tf_style("Correo electrónico",    ft.Icons.MAIL_OUTLINE_ROUNDED)
    password_field= _tf_style("Contraseña",            ft.Icons.LOCK_OUTLINE_ROUNDED, password=True)
    confirm_field = _tf_style("Confirmar contraseña",  ft.Icons.LOCK_OUTLINE_ROUNDED, password=True)
    error_text    = ft.Text("", color="#EF4444", size=12, visible=False)

    register_label = ft.Text(
        "Crear cuenta de estudiante", size=15, weight=ft.FontWeight.W_700,
        color=TK_BACKGROUND, text_align=ft.TextAlign.CENTER,
    )
    register_box = ft.Container(
        expand=True, bgcolor=_accent(), border_radius=14,
        padding=ft.padding.symmetric(vertical=14),
        alignment=ft.Alignment(0, 0),
        content=register_label,
    )
    register_btn = ft.GestureDetector(on_tap=lambda _: None, content=register_box)

    theme_btn = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE_ROUNDED if is_dark[0] else ft.Icons.DARK_MODE_ROUNDED,
        icon_color=_faint(),
    )
    icon_box = ft.Container(
        width=44, height=44, border_radius=12,
        bgcolor=_icon_bg(), alignment=ft.Alignment(0, 0),
        content=ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED, color=_accent(), size=24),
    )
    tab_row     = ft.Container()
    card        = ft.Container(expand=True, border_radius=20, padding=24)
    view        = ft.View(route="/register", bgcolor=_bg(), padding=24)

    def _tab_widget() -> ft.Container:
        def _tab(idx: int, label: str) -> ft.GestureDetector:
            sel = sel_tab[0] == idx
            return ft.GestureDetector(
                on_tap=lambda _: _select_tab(idx),
                content=ft.Container(
                    expand=True,
                    bgcolor=_accent() if sel else ft.Colors.TRANSPARENT,
                    border_radius=10,
                    padding=ft.padding.symmetric(vertical=10),
                    content=ft.Text(
                        label,
                        text_align=ft.TextAlign.CENTER,
                        size=14, weight=ft.FontWeight.W_600,
                        color=TK_BACKGROUND if sel else _text(),
                    ),
                ),
            )
        return ft.Container(
            bgcolor=_surf_alt(), border_radius=14, padding=4,
            content=ft.Row(spacing=0, controls=[_tab(0, "Estudiante"), _tab(1, "Profesor")]),
        )

    def _select_tab(idx: int) -> None:
        sel_tab[0] = idx
        is_teacher = idx == 1
        email_field.hint_text  = "Correo institucional" if is_teacher else "Correo electrónico"
        register_label.value   = "Crear cuenta de profesor" if is_teacher else "Crear cuenta de estudiante"
        tab_row.content        = _tab_widget()
        page.update()

    def _show_error(msg: str) -> None:
        error_text.value   = msg
        error_text.visible = True
        page.update()

    def _notify() -> None:
        vm = student_vm if sel_tab[0] == 0 else teacher_vm
        error_text.value      = vm.auth_error
        error_text.visible    = bool(vm.auth_error)
        loading = vm.is_loading
        register_btn.on_tap   = (lambda _: None) if loading else _on_register
        register_box.bgcolor  = f"{_accent()}66" if loading else _accent()
        register_label.value  = "Creando..." if loading else (
            "Crear cuenta de profesor" if sel_tab[0] == 1 else "Crear cuenta de estudiante"
        )
        page.update()

    student_vm._notify = _notify
    teacher_vm._notify = _notify

    def _on_register(_) -> None:
        name    = name_field.value or ""
        email   = email_field.value or ""
        pwd     = password_field.value or ""
        confirm = confirm_field.value or ""
        if not name.strip() or not email.strip() or not pwd:
            _show_error("Completa todos los campos"); return
        if pwd != confirm:
            _show_error("Las contraseñas no coinciden"); return
        is_teacher = sel_tab[0] == 1

        async def _do() -> None:
            if is_teacher:
                ok = teacher_vm.register(name, email, pwd)
                if ok:
                    await page.push_route("/teacher/dash")
            else:
                ok = student_vm.register(name, email, pwd)
                if ok:
                    await page.push_route("/student/courses")
        page.run_task(_do)

    def _toggle_theme(_) -> None:
        is_dark[0] = not is_dark[0]
        page.theme_mode = ft.ThemeMode.DARK if is_dark[0] else ft.ThemeMode.LIGHT
        theme_btn.icon       = ft.Icons.LIGHT_MODE_ROUNDED if is_dark[0] else ft.Icons.DARK_MODE_ROUNDED
        theme_btn.icon_color = _faint()
        icon_box.bgcolor     = _icon_bg()
        icon_box.content.color = _accent()
        for tf in (name_field, email_field, password_field, confirm_field):
            tf.focused_border_color = _accent()
            tf.border_color         = _border()
            tf.bgcolor              = _surf()
        register_box.bgcolor  = _accent()
        register_label.color  = TK_BACKGROUND
        tab_row.content       = _tab_widget()
        card.bgcolor          = _surf()
        card.border           = ft.Border.all(1, _border())
        view.bgcolor          = _bg()
        page.update()

    register_btn.on_tap  = _on_register
    theme_btn.on_click   = _toggle_theme

    tab_row.content  = _tab_widget()
    card.bgcolor     = _surf()
    card.border      = ft.Border.all(1, _border())
    card.content     = ft.Column(
        scroll=ft.ScrollMode.AUTO, spacing=12,
        controls=[
            ft.Row(controls=[icon_box, ft.Container(expand=True), theme_btn]),
            ft.Text("Crear cuenta", size=26, weight=ft.FontWeight.W_800, color=_text()),
            ft.Text("Desliza para cambiar el tipo de cuenta.", size=13, color=_faint()),
            tab_row,
            name_field,
            email_field,
            password_field,
            confirm_field,
            error_text,
            register_btn,
            ft.Container(height=4),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text("¿Ya tienes cuenta? ", size=13, color=_faint()),
                    ft.GestureDetector(
                        on_tap=lambda _: page.go("/login"),
                        content=ft.Text(
                            "Inicia sesión", size=13,
                            weight=ft.FontWeight.W_700, color=_accent(),
                        ),
                    ),
                ],
            ),
        ],
    )

    view.controls = [ft.SafeArea(expand=True, content=card)]
    return view
