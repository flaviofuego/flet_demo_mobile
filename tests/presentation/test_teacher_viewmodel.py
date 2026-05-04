import pytest
from unittest.mock import MagicMock, patch
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel
from src.domain.models.teacher import Teacher
from src.domain.models.course import CourseModel
from src.domain.models.group_category import GroupCategory, CourseGroup


def _make_vm():
    auth = MagicMock()
    group = MagicMock()
    eval_ = MagicMock()
    course = MagicMock()
    auth.get_current_session.return_value = None
    group.get_all.return_value = []
    eval_.get_all.return_value = []
    course.get_all.return_value = []
    vm = TeacherViewModel(auth, group, eval_, course)
    return vm, auth, group, eval_, course


def test_initial_eval_name_is_empty():
    vm, *_ = _make_vm()
    assert vm.eval_name == ""


def test_reset_eval_form_clears_all_fields():
    vm, *_ = _make_vm()
    vm.eval_name = "Old name"
    vm.selected_course_id = 5
    vm.selected_course_name = "Old course"
    vm.selected_category_id = 3
    vm.selected_category_name = "Old cat"
    vm.categories_for_course = [MagicMock()]
    vm.reset_eval_form()
    assert vm.eval_name == ""
    assert vm.selected_course_id is None
    assert vm.selected_course_name == ""
    assert vm.selected_category_id is None
    assert vm.selected_category_name == ""
    assert vm.categories_for_course == []


def test_check_session_loads_teacher_data():
    vm, auth, group, eval_, course = _make_vm()
    t = Teacher(id="1", name="Ana", email="ana@uni.edu", initials="A")
    auth.get_current_session.return_value = t
    course.get_all.return_value = []
    group.get_all.return_value = []
    eval_.get_all.return_value = []
    vm.check_session()
    assert vm.teacher == t
    assert vm.is_logged_in is True


def test_create_course_prepends_to_list():
    vm, auth, group, eval_, course = _make_vm()
    t = Teacher(id="1", name="Prof", email="p@uni.edu", initials="P")
    vm.teacher = t
    new_course = CourseModel(id=1, name="Math", code="M101", teacher_id=1, created_at=0)
    course.create.return_value = new_course
    vm.create_course("Math", "M101")
    assert vm.courses[0] == new_course
    course.create.assert_called_once_with(name="Math", code="M101", teacher_id=1)


def test_delete_course_removes_from_list():
    vm, auth, group, eval_, course = _make_vm()
    vm.teacher = Teacher(id="1", name="Prof", email="p@uni.edu", initials="P")
    c = CourseModel(id=7, name="Bio", code="B1", teacher_id=1, created_at=0)
    vm.courses = [c]
    vm.delete_course(7)
    assert vm.courses == []
    course.delete.assert_called_once_with(7)


def test_delete_course_clears_selected_if_deleted():
    vm, auth, group, eval_, course = _make_vm()
    vm.teacher = Teacher(id="1", name="Prof", email="p@uni.edu", initials="P")
    c = CourseModel(id=7, name="Bio", code="B1", teacher_id=1, created_at=0)
    vm.courses = [c]
    vm.selected_course_id = 7
    vm.selected_course_name = "Bio"
    vm.delete_course(7)
    assert vm.selected_course_id is None
    assert vm.selected_course_name == ""


def test_create_evaluation_requires_course():
    vm, *_ = _make_vm()
    vm.teacher = Teacher(id="1", name="Prof", email="p@uni.edu", initials="P")
    vm.selected_course_id = None
    vm.selected_category_id = 3
    err = vm.create_evaluation()
    assert err is not None
    assert "curso" in err.lower()


def test_create_evaluation_requires_category():
    vm, *_ = _make_vm()
    vm.teacher = Teacher(id="1", name="Prof", email="p@uni.edu", initials="P")
    vm.selected_course_id = 1
    vm.selected_category_id = None
    err = vm.create_evaluation()
    assert err is not None
    assert "categor" in err.lower()


def test_load_categories_does_not_auto_select():
    """load_categories must NOT auto-select a category — that leaks state into new-eval form."""
    vm, auth, group, eval_, course = _make_vm()
    vm.teacher = Teacher(id="1", name="Prof", email="p@uni.edu", initials="P")
    cat = GroupCategory(id=2, name="Sprint 1", groups=[], imported_at=__import__("datetime").datetime.now(), course_id=0)
    group.get_all.return_value = [cat]
    vm.load_categories()
    assert vm.selected_category_id is None, "load_categories must not auto-select a category"
