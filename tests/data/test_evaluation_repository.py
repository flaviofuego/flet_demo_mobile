import pytest
from datetime import datetime, timedelta
from src.data.services.database_service import DatabaseService
from src.data.repositories.group_repository_impl import GroupRepositoryImpl
from src.data.repositories.evaluation_repository_impl import EvaluationRepositoryImpl

SAMPLE_CSV = """Group Code,Group Name,Section,Username,Last Name,First Name,Last Name
GRP001,Grupo A,001,ana@uni.edu,Lopez,Ana,Lopez
GRP001,Grupo A,001,bob@uni.edu,Smith,Bob,Smith
GRP002,Grupo B,001,carlos@uni.edu,Perez,Carlos,Perez
"""

@pytest.fixture
def setup(tmp_path):
    db = DatabaseService(db_path=str(tmp_path / "test.db"))
    group_repo = GroupRepositoryImpl(db)
    eval_repo = EvaluationRepositoryImpl(db)
    cat = group_repo.import_csv(SAMPLE_CSV, "Sprint 1", teacher_id=1, course_id=0)
    return db, eval_repo, cat


def test_create_evaluation(setup):
    db, eval_repo, cat = setup
    ev = eval_repo.create("Eval 1", cat.id, hours=48, visibility="public", teacher_id=1)
    assert ev.name == "Eval 1"
    assert ev.is_active is True


def test_get_all_evaluations(setup):
    db, eval_repo, cat = setup
    eval_repo.create("Eval 1", cat.id, hours=48, visibility="public", teacher_id=1)
    evals = eval_repo.get_all(teacher_id=1)
    assert len(evals) == 1


def test_rename_evaluation(setup):
    db, eval_repo, cat = setup
    ev = eval_repo.create("Old Name", cat.id, hours=48, visibility="public", teacher_id=1)
    eval_repo.rename(ev.id, "New Name", teacher_id=1)
    evals = eval_repo.get_all(teacher_id=1)
    assert evals[0].name == "New Name"


def test_delete_evaluation(setup):
    db, eval_repo, cat = setup
    ev = eval_repo.create("To Delete", cat.id, hours=48, visibility="public", teacher_id=1)
    eval_repo.delete(ev.id)
    assert eval_repo.get_all(teacher_id=1) == []


def test_get_evaluations_for_student(setup):
    db, eval_repo, cat = setup
    eval_repo.create("Eval 1", cat.id, hours=48, visibility="public", teacher_id=1)
    evals = eval_repo.get_evaluations_for_student("ana@uni.edu")
    assert len(evals) == 1


def test_get_peers_for_student(setup):
    db, eval_repo, cat = setup
    ev = eval_repo.create("Eval 1", cat.id, hours=48, visibility="public", teacher_id=1)
    peers = eval_repo.get_peers_for_student(ev.id, "ana@uni.edu")
    assert len(peers) == 1
    assert peers[0].name == "Bob Smith"


def test_save_and_check_responses(setup):
    db, eval_repo, cat = setup
    ev = eval_repo.create("Eval 1", cat.id, hours=48, visibility="public", teacher_id=1)
    # ana's student_id: find it
    conn = db.connect()
    ana_row = conn.execute("SELECT id FROM students WHERE email='ana@uni.edu'").fetchone()
    bob_row = conn.execute("SELECT id FROM group_members WHERE LOWER(username)='bob@uni.edu'").fetchone()
    ana_id = ana_row["id"]
    bob_member_id = bob_row["id"]
    assert not eval_repo.has_evaluated(ev.id, ana_id, bob_member_id)
    eval_repo.save_responses(ev.id, ana_id, bob_member_id,
                             {"punct": 4, "contrib": 3, "commit": 5, "attitude": 4})
    assert eval_repo.has_evaluated(ev.id, ana_id, bob_member_id)


def test_get_my_results(setup):
    db, eval_repo, cat = setup
    ev = eval_repo.create("Eval 1", cat.id, hours=48, visibility="public", teacher_id=1)
    conn = db.connect()
    bob_member = conn.execute("SELECT id FROM group_members WHERE LOWER(username)='bob@uni.edu'").fetchone()
    ana_student = conn.execute("SELECT id FROM students WHERE email='ana@uni.edu'").fetchone()
    # Ana evaluates Bob
    eval_repo.save_responses(ev.id, ana_student["id"], bob_member["id"],
                             {"punct": 4, "contrib": 4, "commit": 4, "attitude": 4})
    results = eval_repo.get_my_results(ev.id, "bob@uni.edu")
    assert len(results) == 4
    assert all(r.value == 4.0 for r in results)


def test_save_responses_idempotent(setup):
    db, eval_repo, cat = setup
    ev = eval_repo.create("Eval 1", cat.id, hours=48, visibility="public", teacher_id=1)
    conn = db.connect()
    ana = conn.execute("SELECT id FROM students WHERE email='ana@uni.edu'").fetchone()
    bob = conn.execute("SELECT id FROM group_members WHERE LOWER(username)='bob@uni.edu'").fetchone()
    scores = {"punct": 4, "contrib": 3, "commit": 5, "attitude": 4}
    # submit twice — should not duplicate rows
    eval_repo.save_responses(ev.id, ana["id"], bob["id"], scores)
    eval_repo.save_responses(ev.id, ana["id"], bob["id"], scores)
    rows = conn.execute(
        "SELECT COUNT(*) AS cnt FROM evaluation_responses WHERE eval_id=? AND evaluator_id=? AND evaluated_member_id=?",
        (ev.id, ana["id"], bob["id"]),
    ).fetchone()
    assert rows["cnt"] == 4, f"Expected 4 rows (one per criterion), got {rows['cnt']}"
