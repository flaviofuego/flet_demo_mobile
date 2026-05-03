"""EvalUn — application entry point.

Manual dependency injection and Flet router.

Run locally:
    python main.py

Package for mobile:
    flet build apk
    flet build ipa
"""
from __future__ import annotations

import flet as ft

from src.data.services.database_service import DatabaseService
from src.data.repositories.auth_repository_impl import AuthRepositoryImpl
from src.data.repositories.teacher_auth_repository_impl import TeacherAuthRepositoryImpl
from src.data.repositories.unified_auth_repository_impl import UnifiedAuthRepositoryImpl
from src.data.repositories.group_repository_impl import GroupRepositoryImpl
from src.data.repositories.course_repository_impl import CourseRepositoryImpl
from src.data.repositories.evaluation_repository_impl import EvaluationRepositoryImpl

from src.presentation.theme.app_colors import SK_BACKGROUND, SK_PRIMARY, TK_BACKGROUND
from src.presentation.viewmodels.login_viewmodel import LoginViewModel
from src.presentation.viewmodels.student_viewmodel import StudentViewModel
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel

from src.presentation.pages.auth.login_page import login_page
from src.presentation.pages.auth.register_page import register_page
from src.presentation.pages.student.s_courses_page import s_courses_page
from src.presentation.pages.student.s_eval_list_page import s_eval_list_page
from src.presentation.pages.student.s_peers_page import s_peers_page
from src.presentation.pages.student.s_peer_score_page import s_peer_score_page
from src.presentation.pages.student.s_my_results_page import s_my_results_page
from src.presentation.pages.teacher.t_dash_page import t_dash_page
from src.presentation.pages.teacher.t_import_page import t_import_page
from src.presentation.pages.teacher.t_new_eval_page import t_new_eval_page
from src.presentation.pages.teacher.t_results_page import t_results_page
from src.presentation.pages.teacher.t_profile_page import t_profile_page
from src.presentation.pages.teacher.t_course_manage_page import t_course_manage_page


def main(page: ft.Page) -> None:
    page.title = "EvalUn"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0

    # ── Dependency injection ───────────────────────────────────────────────────
    db           = DatabaseService()
    student_auth = AuthRepositoryImpl(db)
    teacher_auth = TeacherAuthRepositoryImpl(db)
    unified_auth = UnifiedAuthRepositoryImpl(student_auth, teacher_auth)
    group_repo   = GroupRepositoryImpl(db)
    course_repo  = CourseRepositoryImpl(db)
    eval_repo    = EvaluationRepositoryImpl(db)

    login_vm   = LoginViewModel(unified_auth)
    student_vm = StudentViewModel(student_auth, eval_repo)
    teacher_vm = TeacherViewModel(teacher_auth, group_repo, eval_repo, course_repo)

    # ── Router ────────────────────────────────────────────────────────────────
    def route_change(e=None) -> None:
        page.views.clear()
        r = page.route

        if r == "/login":
            page.views.append(login_page(page, login_vm, student_vm, teacher_vm))
        elif r == "/register":
            page.views.append(register_page(page, student_vm, teacher_vm))
        elif r == "/student/courses":
            page.views.append(s_courses_page(page, student_vm))
        elif r == "/student/eval-list":
            page.views.append(s_eval_list_page(page, student_vm))
        elif r == "/student/peers":
            page.views.append(s_peers_page(page, student_vm))
        elif r == "/student/peer-score":
            page.views.append(s_peer_score_page(page, student_vm))
        elif r == "/student/results":
            page.views.append(s_my_results_page(page, student_vm))
        elif r == "/teacher/dash":
            page.views.append(t_dash_page(page, teacher_vm))
        elif r == "/teacher/import":
            page.views.append(t_import_page(page, teacher_vm))
        elif r == "/teacher/new-eval":
            page.views.append(t_new_eval_page(page, teacher_vm))
        elif r == "/teacher/results":
            page.views.append(t_results_page(page, teacher_vm))
        elif r == "/teacher/profile":
            page.views.append(t_profile_page(page, teacher_vm))
        elif r == "/teacher/courses":
            page.views.append(t_course_manage_page(page, teacher_vm))
        else:
            page.views.append(_splash_view(page, student_vm, teacher_vm))

        page.update()

    async def view_pop(e: ft.ViewPopEvent) -> None:
        if e.view is not None:
            page.views.remove(e.view)
        if page.views:
            top = page.views[-1]
            await page.push_route(top.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    route_change()  # llamada directa — evita la pantalla negra de page.go() en Flet ≥ 0.80


def _splash_view(
    page: ft.Page,
    student_vm: StudentViewModel,
    teacher_vm: TeacherViewModel,
) -> ft.View:
    async def _resolve() -> None:
        try:
            student_vm.check_session()
            teacher_vm.check_session()
        except Exception:
            pass
        if teacher_vm.is_logged_in:
            await page.push_route("/teacher/dash")
        elif student_vm.is_logged_in:
            await page.push_route("/student/courses")
        else:
            await page.push_route("/login")

    page.run_task(_resolve)

    return ft.View(
        route="/",
        bgcolor=SK_BACKGROUND,
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.Alignment(0, 0),
                content=ft.ProgressRing(color=SK_PRIMARY, stroke_width=2),
            )
        ],
    )


if __name__ == "__main__":
    ft.run(main)
