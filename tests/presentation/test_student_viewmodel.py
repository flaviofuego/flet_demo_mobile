import pytest
from src.data.services.database_service import DatabaseService
from src.data.repositories.auth_repository_impl import AuthRepositoryImpl
from src.data.repositories.evaluation_repository_impl import EvaluationRepositoryImpl
from src.data.repositories.group_repository_impl import GroupRepositoryImpl
from src.presentation.viewmodels.student_viewmodel import StudentViewModel, EvalStudentStatus


# Brightspace-format CSV: col[1]=group name, col[3]=username, col[5]=first, col[6]=last
SAMPLE_CSV = """Group Code,Group Name,Section,Username,Last Name,First Name,Last Name
GRP001,Grupo A,001,ana@uni.edu,Lopez,Ana,Lopez
GRP001,Grupo A,001,bob@uni.edu,Smith,Bob,Smith
"""


@pytest.fixture
def vm(tmp_path):
    db = DatabaseService(db_path=str(tmp_path / "test.db"))
    auth = AuthRepositoryImpl(db)
    eval_repo = EvaluationRepositoryImpl(db)
    return StudentViewModel(auth_repo=auth, eval_repo=eval_repo)


def test_initial_state(vm):
    assert vm.student is None
    assert vm.is_logged_in is False
    assert vm.is_loading is False
    assert vm.evaluations == []


def test_check_session_no_session_leaves_student_none(vm):
    vm.check_session()
    assert vm.student is None


def test_register_sets_student(vm):
    vm.register("Ana López", "ana@uni.edu", "secret123")
    assert vm.student is not None
    assert vm.student.email == "ana@uni.edu"
    assert vm.is_logged_in is True


def test_logout_clears_student(vm):
    vm.register("Ana López", "ana@uni.edu", "secret123")
    vm.logout()
    assert vm.student is None
    assert vm.is_logged_in is False


def test_register_duplicate_email_sets_auth_error(vm):
    vm.register("Ana", "ana@uni.edu", "pass1")
    vm.register("Ana 2", "ana@uni.edu", "pass2")
    assert "registrado" in vm.auth_error.lower()


def test_performance_badge_thresholds():
    from src.domain.models.peer_evaluation import CriterionResult
    vm_bare = StudentViewModel.__new__(StudentViewModel)
    vm_bare._notify = lambda: None
    vm_bare.my_results = [CriterionResult(label="X", value=4.6)]
    assert "Excelente" in vm_bare.performance_badge
    vm_bare.my_results = [CriterionResult(label="X", value=3.6)]
    assert "Buen" in vm_bare.performance_badge
    vm_bare.my_results = [CriterionResult(label="X", value=2.6)]
    assert "adecuado" in vm_bare.performance_badge.lower()
    vm_bare.my_results = [CriterionResult(label="X", value=2.0)]
    assert "Necesita" in vm_bare.performance_badge


def test_set_score_updates_scores(vm):
    vm.scores = {}
    vm.set_score("punct", 4)
    assert vm.scores["punct"] == 4


def test_eval_progress_zero_with_no_peers(vm):
    vm.peers = []
    assert vm.eval_progress == 0.0


# ---------------------------------------------------------------------------
# Integration fixtures and tests — full DB round-trip via real repositories
# ---------------------------------------------------------------------------

@pytest.fixture
def full_setup(tmp_path):
    db = DatabaseService(db_path=str(tmp_path / "test.db"))
    auth_repo = AuthRepositoryImpl(db)
    eval_repo = EvaluationRepositoryImpl(db)
    group_repo = GroupRepositoryImpl(db)
    # Register students first so login with their own password works;
    # import_csv uses INSERT OR IGNORE so it won't overwrite passwords.
    auth_repo.register("Ana Lopez", "ana@uni.edu", "pass")
    auth_repo.register("Bob Smith", "bob@uni.edu", "pass")
    # Import CSV to create group_categories / groups / group_members rows
    cat = group_repo.import_csv(SAMPLE_CSV, "Sprint 1", teacher_id=1, course_id=0)
    # Create an active evaluation (hours=48 keeps it open)
    ev = eval_repo.create("Eval 1", cat.id, hours=48, visibility="public", teacher_id=1)
    vm = StudentViewModel(auth_repo, eval_repo)
    return vm, db, auth_repo, eval_repo, ev


def test_submit_evaluation_saves_responses_to_db(full_setup):
    vm, db, auth_repo, eval_repo, ev = full_setup
    # Log ana in and verify she has evaluations
    auth_repo.login("ana@uni.edu", "pass")
    vm.check_session()
    assert vm.student is not None
    assert vm.evaluations != []
    # Select the eval and load peers; ana sees only bob
    vm.select_eval_for_evaluation(ev)
    assert len(vm.peers) == 1
    bob = vm.peers[0]
    # Score bob on all criteria then save
    vm.select_peer(bob)
    from src.domain.models.peer_evaluation import EvalCriterion
    for c in EvalCriterion.DEFAULTS:
        vm.set_score(c.id, 4)
    vm.save_peer_score()
    assert bob.evaluated is True
    # Submit persists to DB
    vm.submit_evaluation()
    conn = db.connect()
    rows = conn.execute(
        "SELECT COUNT(*) AS cnt FROM evaluation_responses WHERE eval_id=?", (ev.id,)
    ).fetchone()
    assert rows["cnt"] == 4, f"Expected 4 criterion responses, got {rows['cnt']}"


def test_submit_evaluation_is_idempotent(full_setup):
    vm, db, auth_repo, eval_repo, ev = full_setup
    auth_repo.login("ana@uni.edu", "pass")
    vm.check_session()
    vm.select_eval_for_evaluation(ev)
    bob = vm.peers[0]
    vm.select_peer(bob)
    from src.domain.models.peer_evaluation import EvalCriterion
    for c in EvalCriterion.DEFAULTS:
        vm.set_score(c.id, 4)
    vm.save_peer_score()
    vm.submit_evaluation()
    # Second call must not duplicate rows (unique index + INSERT OR REPLACE)
    vm.submit_evaluation()
    conn = db.connect()
    rows = conn.execute(
        "SELECT COUNT(*) AS cnt FROM evaluation_responses WHERE eval_id=?", (ev.id,)
    ).fetchone()
    assert rows["cnt"] == 4, f"Expected 4 after idempotent submit, got {rows['cnt']}"


def test_submit_evaluation_updates_eval_status(full_setup):
    vm, db, auth_repo, eval_repo, ev = full_setup
    auth_repo.login("ana@uni.edu", "pass")
    vm.check_session()
    # Before submission the eval should be pending
    assert vm.eval_statuses.get(ev.id) == EvalStudentStatus.active_pending
    vm.select_eval_for_evaluation(ev)
    bob = vm.peers[0]
    vm.select_peer(bob)
    from src.domain.models.peer_evaluation import EvalCriterion
    for c in EvalCriterion.DEFAULTS:
        vm.set_score(c.id, 4)
    vm.save_peer_score()
    vm.submit_evaluation()
    # After submission the status must flip to completed
    assert vm.eval_statuses.get(ev.id) == EvalStudentStatus.active_completed


def test_select_eval_for_results_loads_my_results(full_setup):
    vm, db, auth_repo, eval_repo, ev = full_setup
    # Bob logs in and scores ana
    auth_repo.login("bob@uni.edu", "pass")
    bob_vm = StudentViewModel(auth_repo, eval_repo)
    bob_vm.check_session()
    bob_vm.select_eval_for_evaluation(ev)
    assert len(bob_vm.peers) == 1
    ana = bob_vm.peers[0]
    bob_vm.select_peer(ana)
    from src.domain.models.peer_evaluation import EvalCriterion
    for c in EvalCriterion.DEFAULTS:
        bob_vm.set_score(c.id, 5)
    bob_vm.save_peer_score()
    bob_vm.submit_evaluation()
    # Ana logs in and checks her results
    auth_repo.login("ana@uni.edu", "pass")
    vm2 = StudentViewModel(auth_repo, eval_repo)
    vm2.check_session()
    vm2.select_eval_for_results(ev)
    assert vm2.my_results != [], "Ana should have criterion results after being scored by Bob"
    assert vm2.my_average > 0, "Ana's average should be positive"
