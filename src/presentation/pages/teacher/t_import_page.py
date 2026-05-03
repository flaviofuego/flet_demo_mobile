"""TImportPage — CSV import of groups."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER,
    TK_TEXT, TK_TEXT_FAINT, TK_GOLD, TK_DANGER, TK_SUCCESS,
)
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def t_import_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content = ft.Container(expand=True)
    state = {"csv_content": None, "filename": "", "course_id": None}

    category_name_field = ft.TextField(
        label="Nombre de la categoría de grupos",
        hint_text="Ej: Sprint 1",
        focused_border_color=TK_GOLD,
    )
    error_text   = ft.Text("", color=TK_DANGER,  size=12, visible=False)
    success_text = ft.Text("", color=TK_SUCCESS, size=12, visible=False)

    file_picker = ft.FilePicker()

    async def _pick_file(_) -> None:
        files = await file_picker.pick_files(allowed_extensions=["csv"], allow_multiple=False)
        if not files:
            return
        f = files[0]
        state["filename"] = f.name
        try:
            with open(f.path, "r", encoding="utf-8-sig") as fh:
                state["csv_content"] = fh.read()
            error_text.visible = False
        except Exception as ex:
            error_text.value   = f"Error leyendo archivo: {ex}"
            error_text.visible = True
        _refresh()

    def _course_picker() -> ft.BottomSheet:
        def _pick(cid: int, cname: str) -> None:
            state["course_id"] = cid
            page.pop_dialog()
            _refresh()

        def _create_new(_) -> None:
            nf = ft.TextField(label="Nombre del curso", autofocus=True)
            cf = ft.TextField(label="Código (opcional)")
            def _do(_) -> None:
                if not nf.value:
                    return
                vm.create_course(nf.value, cf.value or "")
                # pick the newest course
                if vm.courses:
                    _pick(vm.courses[0].id, vm.courses[0].name)
                page.pop_dialog()
            cdlg = ft.AlertDialog(
                title=ft.Text("Nuevo curso"),
                content=ft.Column(tight=True, controls=[nf, cf]),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                    ft.Button("Crear", on_click=_do,
                                     style=ft.ButtonStyle(bgcolor=TK_GOLD, color=TK_BACKGROUND)),
                ],
            )
            page.show_dialog(cdlg)

        tiles = [
            ft.ListTile(title=ft.Text(c.name, color=TK_TEXT),
                       subtitle=ft.Text(c.code, color=TK_TEXT_FAINT, size=11) if c.code else None,
                       on_click=lambda _, cid=c.id, cn=c.name: _pick(cid, cn))
            for c in vm.courses
        ]
        bs = ft.BottomSheet(
            open=True,
            content=ft.Container(bgcolor=TK_SURFACE, padding=16,
                                content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[
                                    ft.Text("Selecciona un curso", size=16,
                                           weight=ft.FontWeight.W_700, color=TK_TEXT),
                                    ft.Divider(color=TK_BORDER),
                                    ft.ListTile(
                                        leading=ft.Icon(ft.Icons.ADD, color=TK_GOLD),
                                        title=ft.Text("Crear nuevo curso", color=TK_GOLD),
                                        on_click=_create_new,
                                    ),
                                    *tiles,
                                ])),
        )
        return bs

    def _do_import() -> None:
        csv_content   = state["csv_content"]
        cat_name      = (category_name_field.value or "").strip()
        course_id     = state["course_id"]
        if not csv_content:
            error_text.value = "Selecciona un archivo CSV primero"
            error_text.visible = True
            page.update(); return
        if not cat_name:
            error_text.value = "Ingresa un nombre de categoría"
            error_text.visible = True
            page.update(); return
        if course_id is None:
            error_text.value = "Selecciona un curso"
            error_text.visible = True
            page.update(); return

        def _run() -> None:
            vm.import_csv(csv_content, cat_name, course_id)
            if vm.import_error:
                error_text.value   = vm.import_error
                error_text.visible = True
                success_text.visible = False
            else:
                success_text.value   = f"'{cat_name}' importada correctamente"
                success_text.visible = True
                error_text.visible   = False
                state.update({"csv_content": None, "filename": "", "course_id": None})
                category_name_field.value = ""
            page.update()

        page.run_thread(_run)

    def _category_tile(cat) -> ft.Container:
        def _delete(_) -> None:
            dlg = ft.AlertDialog(
                title=ft.Text("¿Eliminar categoría?"),
                content=ft.Text(f"'{cat.name}' y todos sus grupos serán eliminados."),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                    ft.Button("Eliminar",
                                     style=ft.ButtonStyle(bgcolor=TK_DANGER, color="#FFFFFF"),
                                     on_click=lambda _: (vm.delete_category(cat.id), page.pop_dialog())),
                ],
            )
            page.show_dialog(dlg)
        return ft.Container(
            bgcolor=TK_SURFACE, border_radius=12,
            border=ft.Border.all(1, TK_BORDER),
            padding=12, margin=ft.margin.only(bottom=8),
            content=ft.Row(controls=[
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text(cat.name, size=13, weight=ft.FontWeight.W_600, color=TK_TEXT),
                    ft.Text(f"{cat.group_count} grupos · {cat.member_count} miembros",
                           size=11, color=TK_TEXT_FAINT),
                ]),
                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=TK_DANGER, on_click=_delete),
            ]),
        )

    def _build_body() -> ft.Control:
        filename    = state["filename"]
        course_id   = state["course_id"]
        course_name = ""
        if course_id is not None:
            c = next((c for c in vm.courses if c.id == course_id), None)
            course_name = c.name if c else ""

        import_section = ft.Column(spacing=10, controls=[
            ft.Text("IMPORTAR GRUPOS", size=10, weight=ft.FontWeight.W_600,
                   color=TK_TEXT_FAINT),
            ft.Container(bgcolor=TK_SURFACE, border_radius=14,
                        border=ft.Border.all(1, TK_BORDER), padding=16,
                        content=ft.Column(spacing=10, controls=[
                            ft.Button(
                                f"📄 {filename}" if filename else "Seleccionar CSV",
                                style=ft.ButtonStyle(
                                    bgcolor=TK_GOLD if filename else TK_SURFACE_ALT,
                                    color=TK_BACKGROUND if filename else TK_TEXT_FAINT,
                                ),
                                on_click=_pick_file,
                            ),
                            ft.Button(
                                f"📚 {course_name}" if course_name else "Seleccionar curso",
                                style=ft.ButtonStyle(
                                    bgcolor=TK_GOLD if course_name else TK_SURFACE_ALT,
                                    color=TK_BACKGROUND if course_name else TK_TEXT_FAINT,
                                ),
                                on_click=lambda _: page.show_dialog(_course_picker()),
                            ),
                            category_name_field,
                            error_text,
                            success_text,
                            ft.Button(
                                "Importando..." if vm.import_loading else "Importar",
                                disabled=vm.import_loading,
                                style=ft.ButtonStyle(bgcolor=TK_GOLD, color=TK_BACKGROUND),
                                expand=True,
                                on_click=lambda _: _do_import(),
                            ),
                        ])),
        ])

        cats_section = ft.Column(spacing=8, controls=[
            ft.Container(height=16),
            ft.Text("CATEGORÍAS IMPORTADAS", size=10, weight=ft.FontWeight.W_600,
                   color=TK_TEXT_FAINT),
            *(
                [ft.Text("Sin categorías importadas", color=TK_TEXT_FAINT, size=12)]
                if not vm.categories
                else [_category_tile(c) for c in vm.categories]
            ),
        ])

        return ft.ListView(controls=[import_section, cats_section], expand=True,
                          padding=ft.padding.symmetric(horizontal=16, vertical=12))

    def _refresh() -> None:
        content.content = _build_body()
        page.update()

    def _notify() -> None:
        _refresh()

    vm._notify = _notify
    content.content = _build_body()

    return ft.View(
        route="/teacher/import",
        bgcolor=TK_BACKGROUND,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK,
                                 on_click=lambda _: page.go("/teacher/dash")),
            title=ft.Text("Importar grupos", color=TK_TEXT),
            bgcolor=TK_BACKGROUND, elevation=0,
        ),
        controls=[content],
        services=[file_picker],
    )
