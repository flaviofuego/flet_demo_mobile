from __future__ import annotations
from enum import Enum
from typing import Callable
from src.domain.models.evaluation import Evaluation
from src.domain.models.peer_evaluation import Peer, CriterionResult, EvalCriterion
from src.domain.models.student import Student
from src.domain.repositories.i_auth_repository import IAuthRepository
from src.domain.repositories.i_evaluation_repository import IEvaluationRepository


class EvalStudentStatus(Enum):
    active_pending   = "active_pending"
    active_completed = "active_completed"
    closed_not_done  = "closed_not_done"
    closed_completed = "closed_completed"


class StudentViewModel:
    def __init__(
        self,
        auth_repo: IAuthRepository,
        eval_repo: IEvaluationRepository,
        notify: Callable[[], None] | None = None,
    ) -> None:
        self._auth = auth_repo
        self._eval = eval_repo
        self._notify = notify or (lambda: None)

        self.student: Student | None = None
        self.is_loading: bool = False
        self.auth_error: str = ""

        self.evaluations: list[Evaluation] = []
        self.eval_statuses: dict[int, EvalStudentStatus] = {}
        self.active_eval: Evaluation | None = None
        self.current_group_name: str = ""
        self.has_active_eval: bool = False

        self.peers: list[Peer] = []
        self.current_peer: Peer | None = None
        self.scores: dict[str, int] = {}
        self.my_results: list[CriterionResult] = []

    @property
    def is_logged_in(self) -> bool:
        return self.student is not None

    @property
    def done_count(self) -> int:
        return sum(1 for p in self.peers if p.evaluated)

    @property
    def total_peers(self) -> int:
        return len(self.peers)

    @property
    def eval_progress(self) -> float:
        return 0.0 if self.total_peers == 0 else self.done_count / self.total_peers

    @property
    def all_evaluated(self) -> bool:
        return self.total_peers > 0 and self.done_count == self.total_peers

    @property
    def all_criteria_scored(self) -> bool:
        return all(c.id in self.scores for c in EvalCriterion.DEFAULTS)

    @property
    def my_average(self) -> float:
        if not self.my_results:
            return 0.0
        return sum(r.value for r in self.my_results) / len(self.my_results)

    @property
    def performance_badge(self) -> str:
        avg = self.my_average
        if avg >= 4.5:
            return "Excelente desempeño"
        if avg >= 3.5:
            return "Buen desempeño"
        if avg >= 2.5:
            return "Desempeño adecuado"
        return "Necesita mejorar"

    def check_session(self) -> None:
        self.is_loading = True
        self._notify()
        try:
            self.student = self._auth.get_current_session()
            if self.student:
                self._load_eval_data()
        finally:
            self.is_loading = False
            self._notify()

    def register(self, name: str, email: str, password: str) -> bool:
        self.is_loading = True
        self.auth_error = ""
        self._notify()
        try:
            self.student = self._auth.register(name, email, password)
            self._load_eval_data()
            return True
        except Exception:
            self.auth_error = "El correo ya está registrado"
            return False
        finally:
            self.is_loading = False
            self._notify()

    def logout(self) -> None:
        self._auth.logout()
        self.student = None
        self._reset_eval_state()
        self._notify()

    def _load_eval_data(self) -> None:
        s = self.student
        if s is None:
            return
        student_id = int(s.id)
        try:
            eval_list = self._eval.get_evaluations_for_student(s.email)
            self.evaluations = eval_list
        except Exception:
            eval_list = []
            self.evaluations = []
        self._compute_statuses(eval_list, s.email, student_id)
        eval_ctx = (
            next((e for e in eval_list if self.eval_statuses.get(e.id) == EvalStudentStatus.active_pending), None)
            or next((e for e in eval_list if e.is_active), None)
            or (eval_list[0] if eval_list else None)
        )
        self.active_eval = eval_ctx
        if eval_ctx is None:
            self.has_active_eval = False
            self.peers = []
            self.my_results = []
            self.current_group_name = ""
            return
        self.has_active_eval = eval_ctx.is_active
        self._load_group_and_peers(eval_ctx, s)
        self._load_my_results(eval_ctx.id, s.email)

    def _compute_statuses(self, eval_list: list[Evaluation], email: str, student_id: int) -> None:
        statuses: dict[int, EvalStudentStatus] = {}
        for ev in eval_list:
            try:
                completed = self._eval.has_completed_all_peers(eval_id=ev.id, email=email, student_id=student_id)
                if ev.is_active:
                    statuses[ev.id] = EvalStudentStatus.active_completed if completed else EvalStudentStatus.active_pending
                else:
                    statuses[ev.id] = EvalStudentStatus.closed_completed if completed else EvalStudentStatus.closed_not_done
            except Exception:
                statuses[ev.id] = EvalStudentStatus.active_pending if ev.is_active else EvalStudentStatus.closed_not_done
        self.eval_statuses = statuses

    def _load_group_and_peers(self, ev: Evaluation, s: Student) -> None:
        try:
            gname = self._eval.get_group_name_for_student(ev.id, s.email)
            self.current_group_name = gname or ev.category_name
        except Exception:
            self.current_group_name = ev.category_name
        student_id = int(s.id)
        try:
            peer_list = self._eval.get_peers_for_student(ev.id, s.email)
            for p in peer_list:
                p.evaluated = self._eval.has_evaluated(
                    eval_id=ev.id, evaluator_student_id=student_id, evaluated_member_id=int(p.id)
                )
        except Exception:
            peer_list = []
        self.peers = peer_list

    def _load_my_results(self, eval_id: int, email: str) -> None:
        try:
            self.my_results = self._eval.get_my_results(eval_id, email)
        except Exception:
            self.my_results = []

    def select_eval_for_evaluation(self, ev: Evaluation) -> None:
        s = self.student
        if s is None:
            return
        self.active_eval = ev
        self.has_active_eval = ev.is_active
        self.peers = []
        self.my_results = []
        self._load_group_and_peers(ev, s)
        self._notify()

    def select_eval_for_results(self, ev: Evaluation) -> None:
        s = self.student
        if s is None:
            return
        self.active_eval = ev
        try:
            gname = self._eval.get_group_name_for_student(ev.id, s.email)
            self.current_group_name = gname or ev.category_name
        except Exception:
            self.current_group_name = ev.category_name
        self._load_my_results(ev.id, s.email)
        self._notify()

    def select_peer(self, peer: Peer) -> None:
        self.current_peer = peer
        self.scores = dict(peer.scores)
        self._notify()

    def set_score(self, criterion_id: str, score: int) -> None:
        self.scores[criterion_id] = score

    def save_peer_score(self) -> None:
        peer = self.current_peer
        if peer is None or not self.all_criteria_scored:
            return
        peer.scores = dict(self.scores)
        peer.evaluated = True
        self._notify()

    def submit_evaluation(self) -> None:
        s = self.student
        ev = self.active_eval
        if s is None or ev is None:
            return
        student_id = int(s.id)
        for peer in self.peers:
            if peer.evaluated and peer.scores:
                try:
                    self._eval.save_responses(
                        eval_id=ev.id, evaluator_student_id=student_id,
                        evaluated_member_id=int(peer.id), scores=peer.scores,
                    )
                except Exception:
                    pass
        self._load_my_results(ev.id, s.email)
        try:
            completed = self._eval.has_completed_all_peers(eval_id=ev.id, email=s.email, student_id=student_id)
            if ev.is_active:
                self.eval_statuses[ev.id] = EvalStudentStatus.active_completed if completed else EvalStudentStatus.active_pending
            else:
                self.eval_statuses[ev.id] = EvalStudentStatus.closed_completed if completed else EvalStudentStatus.closed_not_done
        except Exception:
            pass
        self._notify()

    def _reset_eval_state(self) -> None:
        self.active_eval = None
        self.has_active_eval = False
        self.current_group_name = ""
        self.evaluations = []
        self.eval_statuses = {}
        self.peers = []
        self.my_results = []
        self.current_peer = None
        self.scores = {}
