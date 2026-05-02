import pytest
from src.data.services.database_service import DatabaseService
from src.data.repositories.auth_repository_impl import AuthRepositoryImpl
from src.data.repositories.evaluation_repository_impl import EvaluationRepositoryImpl
from src.presentation.viewmodels.student_viewmodel import StudentViewModel, EvalStudentStatus


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
