import sqlite3
import pytest
from src.data.services.database_service import DatabaseService


@pytest.fixture
def db_service(tmp_path):
    svc = DatabaseService(db_path=str(tmp_path / "test.db"))
    return svc


def test_database_creates_all_tables(db_service):
    db = db_service.connect()
    cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    expected = {
        "students", "sessions", "teachers", "teacher_sessions",
        "courses", "group_categories", "groups", "group_members",
        "evaluations", "evaluation_responses",
    }
    assert expected.issubset(tables)


def test_connect_returns_same_connection(db_service):
    c1 = db_service.connect()
    c2 = db_service.connect()
    assert c1 is c2


def test_students_table_has_unique_email(db_service):
    db = db_service.connect()
    db.execute(
        "INSERT INTO students (name, email, password, initials) VALUES (?,?,?,?)",
        ("Ana", "ana@uni.edu", "hash", "A"),
    )
    db.commit()
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO students (name, email, password, initials) VALUES (?,?,?,?)",
            ("Ana2", "ana@uni.edu", "hash2", "A2"),
        )


def test_schema_version_is_7(tmp_path):
    db = DatabaseService(db_path=str(tmp_path / "test.db"))
    conn = db.connect()
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    assert version == 7


def test_evaluation_responses_has_unique_constraint(tmp_path):
    db = DatabaseService(db_path=str(tmp_path / "test.db"))
    conn = db.connect()
    # Insert prerequisite rows to satisfy FK constraints
    conn.execute(
        "INSERT INTO group_categories (name, imported_at, teacher_id, course_id) VALUES ('Cat', 0, 1, 0)"
    )
    conn.execute(
        "INSERT INTO evaluations (name, category_id, hours, visibility, created_at, closes_at, teacher_id) "
        "VALUES ('E', 1, 48, 'public', 1000, 2000, 1)"
    )
    conn.execute(
        "INSERT OR REPLACE INTO evaluation_responses (eval_id, evaluator_id, evaluated_member_id, criterion_id, score) "
        "VALUES (1, 1, 1, 'punct', 4)"
    )
    # Second INSERT OR REPLACE should update, not duplicate
    conn.execute(
        "INSERT OR REPLACE INTO evaluation_responses (eval_id, evaluator_id, evaluated_member_id, criterion_id, score) "
        "VALUES (1, 1, 1, 'punct', 5)"
    )
    conn.commit()
    rows = conn.execute(
        "SELECT COUNT(*) AS cnt, score FROM evaluation_responses WHERE eval_id=1 AND criterion_id='punct'"
    ).fetchone()
    assert rows["cnt"] == 1
    assert rows["score"] == 5


def test_courses_table_exists_with_correct_columns(db_service):
    db = db_service.connect()
    cursor = db.execute("PRAGMA table_info(courses)")
    cols = {row[1] for row in cursor.fetchall()}
    assert {"id", "teacher_id", "name", "code", "created_at"}.issubset(cols)


def test_group_categories_has_course_id(db_service):
    db = db_service.connect()
    cursor = db.execute("PRAGMA table_info(group_categories)")
    cols = {row[1] for row in cursor.fetchall()}
    assert "course_id" in cols
    assert "teacher_id" in cols
