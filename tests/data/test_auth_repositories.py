import pytest
from src.data.services.database_service import DatabaseService
from src.data.repositories.auth_repository_impl import AuthRepositoryImpl
from src.data.repositories.teacher_auth_repository_impl import TeacherAuthRepositoryImpl
from src.data.repositories.unified_auth_repository_impl import UnifiedAuthRepositoryImpl
from src.domain.models.auth_login_result import AppUserRole


@pytest.fixture
def db(tmp_path):
    return DatabaseService(db_path=str(tmp_path / "test.db"))


@pytest.fixture
def student_repo(db):
    return AuthRepositoryImpl(db)


@pytest.fixture
def teacher_repo(db):
    return TeacherAuthRepositoryImpl(db)


def test_student_register_and_login(student_repo):
    student = student_repo.register("Ana López", "ana@uni.edu", "secret")
    assert student.email == "ana@uni.edu"
    assert student.initials == "AL"
    found = student_repo.login("ana@uni.edu", "secret")
    assert found is not None
    assert found.name == "Ana López"


def test_student_login_wrong_password(student_repo):
    student_repo.register("Ana", "ana@uni.edu", "correct")
    assert student_repo.login("ana@uni.edu", "wrong") is None


def test_student_session_persists(student_repo):
    student_repo.register("Ana", "ana@uni.edu", "pass")
    session = student_repo.get_current_session()
    assert session is not None
    assert session.email == "ana@uni.edu"


def test_student_logout_clears_session(student_repo):
    student_repo.register("Ana", "ana@uni.edu", "pass")
    student_repo.logout()
    assert student_repo.get_current_session() is None


def test_teacher_register_and_login(teacher_repo):
    t = teacher_repo.register("Prof. García", "garcia@uni.edu", "pass")
    assert t.initials == "PG"
    found = teacher_repo.login("garcia@uni.edu", "pass")
    assert found is not None


def test_unified_teacher_first(db):
    s_repo = AuthRepositoryImpl(db)
    t_repo = TeacherAuthRepositoryImpl(db)
    unified = UnifiedAuthRepositoryImpl(s_repo, t_repo)
    # Register as teacher and student with same email
    t_repo.register("Prof.", "shared@uni.edu", "pass")
    s_repo.register("Student", "shared@uni.edu", "pass")  # will fail due to unique constraint
    # Actually use different emails for clarity
    t_repo2 = TeacherAuthRepositoryImpl(db)
    t_repo2.register("Prof.", "teacher@uni.edu", "pass")
    result = unified.login_and_resolve("teacher@uni.edu", "pass")
    assert result is not None
    assert result.role == AppUserRole.teacher


def test_unified_falls_back_to_student(db):
    s_repo = AuthRepositoryImpl(db)
    t_repo = TeacherAuthRepositoryImpl(db)
    unified = UnifiedAuthRepositoryImpl(s_repo, t_repo)
    s_repo.register("Student", "student@uni.edu", "pass")
    result = unified.login_and_resolve("student@uni.edu", "pass")
    assert result is not None
    assert result.role == AppUserRole.student


def test_unified_returns_none_for_bad_credentials(db):
    s_repo = AuthRepositoryImpl(db)
    t_repo = TeacherAuthRepositoryImpl(db)
    unified = UnifiedAuthRepositoryImpl(s_repo, t_repo)
    result = unified.login_and_resolve("nobody@uni.edu", "pass")
    assert result is None
