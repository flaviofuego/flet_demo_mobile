import pytest
from src.data.services.database_service import DatabaseService
from src.data.repositories.course_repository_impl import CourseRepositoryImpl


@pytest.fixture
def repo(tmp_path):
    db = DatabaseService(db_path=str(tmp_path / "test.db"))
    return CourseRepositoryImpl(db)


def test_create_and_get_course(repo):
    course = repo.create("Ingeniería de Software", "IS101", teacher_id=1)
    assert course.name == "Ingeniería de Software"
    assert course.code == "IS101"
    assert course.teacher_id == 1
    courses = repo.get_all(teacher_id=1)
    assert len(courses) == 1
    assert courses[0].id == course.id


def test_delete_course(repo):
    course = repo.create("Curso A", "CA001", teacher_id=1)
    repo.delete(course.id)
    assert repo.get_all(teacher_id=1) == []


def test_get_all_filters_by_teacher(repo):
    repo.create("Curso A", "A001", teacher_id=1)
    repo.create("Curso B", "B001", teacher_id=2)
    assert len(repo.get_all(teacher_id=1)) == 1
    assert len(repo.get_all(teacher_id=2)) == 1
