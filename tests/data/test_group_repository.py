import pytest
from src.data.services.database_service import DatabaseService
from src.data.repositories.group_repository_impl import GroupRepositoryImpl

SAMPLE_CSV = """Group Code,Group Name,Section,Username,Last Name,First Name,Last Name
GRP001,Grupo A,001,ana@uni.edu,Lopez,Ana,Lopez
GRP001,Grupo A,001,bob@uni.edu,Smith,Bob,Smith
GRP002,Grupo B,001,carlos@uni.edu,Perez,Carlos,Perez
"""

@pytest.fixture
def repo(tmp_path):
    db = DatabaseService(db_path=str(tmp_path / "test.db"))
    return GroupRepositoryImpl(db)


def test_import_csv_creates_category(repo):
    cat = repo.import_csv(SAMPLE_CSV, "Sprint 1", teacher_id=1, course_id=0)
    assert cat.name == "Sprint 1"
    assert cat.group_count == 2
    assert cat.member_count == 3


def test_import_csv_creates_students(repo):
    repo.import_csv(SAMPLE_CSV, "Sprint 1", teacher_id=1, course_id=0)
    # Students should be auto-created with default password
    conn = repo._conn()
    row = conn.execute("SELECT * FROM students WHERE email='ana@uni.edu'").fetchone()
    assert row is not None


def test_get_all_returns_categories(repo):
    repo.import_csv(SAMPLE_CSV, "Sprint 1", teacher_id=1, course_id=0)
    cats = repo.get_all(teacher_id=1)
    assert len(cats) == 1
    assert cats[0].name == "Sprint 1"


def test_delete_removes_category(repo):
    cat = repo.import_csv(SAMPLE_CSV, "Sprint 1", teacher_id=1, course_id=0)
    repo.delete(cat.id)
    assert repo.get_all(teacher_id=1) == []


def test_empty_csv_raises(repo):
    with pytest.raises(ValueError):
        repo.import_csv("", "Sprint 1", teacher_id=1, course_id=0)
