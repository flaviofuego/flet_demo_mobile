from __future__ import annotations
from typing import Callable
from src.domain.models.course import CourseModel
from src.domain.models.evaluation import Evaluation
from src.domain.models.group_category import GroupCategory
from src.domain.models.teacher import Teacher
from src.domain.models.teacher_data import GroupResult
from src.domain.repositories.i_teacher_auth_repository import ITeacherAuthRepository
from src.domain.repositories.i_group_repository import IGroupRepository
from src.domain.repositories.i_evaluation_repository import IEvaluationRepository
from src.domain.repositories.i_course_repository import ICourseRepository


class TeacherViewModel:
    def __init__(
        self,
        auth_repo: ITeacherAuthRepository,
        group_repo: IGroupRepository,
        eval_repo: IEvaluationRepository,
        course_repo: ICourseRepository,
        notify: Callable[[], None] | None = None,
    ) -> None:
        self._auth = auth_repo
        self._group = group_repo
        self._eval = eval_repo
        self._course = course_repo
        self._notify = notify or (lambda: None)

        self.teacher: Teacher | None = None
        self.is_loading: bool = False
        self.auth_error: str = ""

        self.courses: list[CourseModel] = []
        self.selected_course_id: int | None = None
        self.selected_course_name: str = ""
        self.categories_for_course: list[GroupCategory] = []

        self.categories: list[GroupCategory] = []
        self.import_loading: bool = False
        self.import_error: str = ""

        self.evaluations: list[Evaluation] = []
        self.active_eval: Evaluation | None = None

        self.eval_name: str = ""
        self.selected_hours: int = 48
        self.selected_visibility: str = "private"
        self.selected_category_id: int | None = None
        self.selected_category_name: str = ""
        self.eval_error: str = ""

        self.group_results: list[GroupResult] = []
        self.results_loading: bool = False
        self.selected_eval_for_results: Evaluation | None = None
        self.drill_group_index: int | None = None

    @property
    def is_logged_in(self) -> bool:
        return self.teacher is not None

    @property
    def total_groups(self) -> int:
        return sum(c.group_count for c in self.categories)

    @property
    def overall_average(self) -> float:
        non_zero = [g.average for g in self.group_results if g.average > 0]
        return round(sum(non_zero) / len(non_zero), 1) if non_zero else 0.0

    def check_session(self) -> None:
        self.is_loading = True
        self._notify()
        try:
            self.teacher = self._auth.get_current_session()
            if self.teacher:
                self._on_login()
        finally:
            self.is_loading = False
            self._notify()

    def register(self, name: str, email: str, password: str) -> bool:
        self.is_loading = True
        self.auth_error = ""
        self._notify()
        try:
            self.teacher = self._auth.register(name, email, password)
            self._on_login()
            return True
        except Exception:
            self.auth_error = "El correo ya está registrado"
            return False
        finally:
            self.is_loading = False
            self._notify()

    def logout(self) -> None:
        self._auth.logout()
        self.teacher = None
        self._notify()

    def _on_login(self) -> None:
        self.load_courses()
        self.load_categories()
        self.load_evaluations()

    def _teacher_id(self) -> int:
        return int(self.teacher.id) if self.teacher else 0

    def load_courses(self) -> None:
        try:
            self.courses = self._course.get_all(self._teacher_id())
        except Exception:
            self.courses = []
        self._notify()

    def create_course(self, name: str, code: str) -> None:
        course = self._course.create(name=name, code=code, teacher_id=self._teacher_id())
        self.courses.insert(0, course)
        self._notify()

    def delete_course(self, course_id: int) -> None:
        self._course.delete(course_id)
        self.courses = [c for c in self.courses if c.id != course_id]
        if self.selected_course_id == course_id:
            self.selected_course_id = None
            self.selected_course_name = ""
            self.categories_for_course = []
        self._notify()

    def load_categories_for_course(self, course_id: int) -> None:
        self.selected_course_id = course_id
        course = next((c for c in self.courses if c.id == course_id), None)
        self.selected_course_name = course.name if course else ""
        try:
            cats = self._course.get_categories_for_course(course_id)
            if not cats:
                # CSV import stores course_id=0; fall back to all teacher categories
                cats = self._group.get_all(self._teacher_id())
            self.categories_for_course = cats
        except Exception:
            self.categories_for_course = list(self.categories)
        self._notify()

    def load_categories(self) -> None:
        try:
            self.categories = self._group.get_all(self._teacher_id())
        except Exception:
            self.categories = []
        self._notify()

    def reset_eval_form(self) -> None:
        self.eval_name = ""
        self.selected_course_id = None
        self.selected_course_name = ""
        self.selected_category_id = None
        self.selected_category_name = ""
        self.categories_for_course = []
        self.selected_hours = 48
        self.selected_visibility = "private"
        self.eval_error = ""

    def import_csv(self, csv_content: str, category_name: str, course_id: int) -> None:
        self.import_loading = True
        self.import_error = ""
        self._notify()
        try:
            cat = self._group.import_csv(csv_content, category_name, self._teacher_id(), course_id)
            self.categories.insert(0, cat)
            if self.selected_category_id is None:
                self.selected_category_id = cat.id
                self.selected_category_name = cat.name
        except Exception as e:
            self.import_error = f"Error al importar: {e}"
        finally:
            self.import_loading = False
            self._notify()

    def delete_category(self, category_id: int) -> None:
        self._group.delete(category_id)
        self.categories = [c for c in self.categories if c.id != category_id]
        if self.selected_category_id == category_id:
            self.selected_category_id = self.categories[0].id if self.categories else None
            self.selected_category_name = self.categories[0].name if self.categories else ""
        self._notify()

    def load_evaluations(self) -> None:
        try:
            all_evals = self._eval.get_all(self._teacher_id())
            self.evaluations = all_evals
            self.active_eval = next((e for e in all_evals if e.is_active), None)
        except Exception:
            self.evaluations = []
            self.active_eval = None
        self._notify()

    def create_evaluation(self) -> str | None:
        """Returns None on success, error message on failure."""
        if self.selected_course_id is None:
            return "Selecciona un curso"
        if self.selected_category_id is None:
            return "Selecciona una categoría de grupos"
        self.is_loading = True
        self.eval_error = ""
        self._notify()
        try:
            ev = self._eval.create(
                name=self.eval_name,
                category_id=self.selected_category_id,
                hours=self.selected_hours,
                visibility=self.selected_visibility,
                teacher_id=self._teacher_id(),
            )
            self.evaluations.insert(0, ev)
            if ev.is_active:
                self.active_eval = ev
            return None
        except Exception as e:
            self.eval_error = str(e)
            return str(e)
        finally:
            self.is_loading = False
            self._notify()

    def rename_evaluation(self, eval_id: int, new_name: str) -> None:
        self._eval.rename(eval_id, new_name, self._teacher_id())
        self.evaluations = [
            Evaluation(
                id=e.id, name=new_name if e.id == eval_id else e.name,
                category_id=e.category_id, category_name=e.category_name,
                course_name=e.course_name, hours=e.hours, visibility=e.visibility,
                created_at=e.created_at, closes_at=e.closes_at,
            )
            for e in self.evaluations
        ]
        if self.active_eval and self.active_eval.id == eval_id:
            self.active_eval = next((e for e in self.evaluations if e.id == eval_id), None)
        self._notify()

    def delete_evaluation(self, eval_id: int) -> None:
        self._eval.delete(eval_id)
        self.evaluations = [e for e in self.evaluations if e.id != eval_id]
        if self.active_eval and self.active_eval.id == eval_id:
            self.active_eval = next((e for e in self.evaluations if e.is_active), None)
        self._notify()

    def load_group_results(self, ev: Evaluation) -> None:
        self.selected_eval_for_results = ev
        self.drill_group_index = None
        self.results_loading = True
        self._notify()
        try:
            self.group_results = self._eval.get_group_results(ev.id)
        except Exception:
            self.group_results = []
        finally:
            self.results_loading = False
            self._notify()
