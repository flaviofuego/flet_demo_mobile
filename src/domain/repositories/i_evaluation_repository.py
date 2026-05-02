from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.models.evaluation import Evaluation
from src.domain.models.peer_evaluation import Peer, CriterionResult
from src.domain.models.teacher_data import GroupResult


class IEvaluationRepository(ABC):

    @abstractmethod
    def create(
        self,
        name: str,
        category_id: int,
        hours: int,
        visibility: str,
        teacher_id: int,
    ) -> Evaluation: ...

    @abstractmethod
    def get_all(self, teacher_id: int) -> list[Evaluation]: ...

    @abstractmethod
    def rename(self, eval_id: int, new_name: str, teacher_id: int) -> None: ...

    @abstractmethod
    def delete(self, eval_id: int) -> None: ...

    @abstractmethod
    def get_evaluations_for_student(self, email: str) -> list[Evaluation]: ...

    @abstractmethod
    def get_group_name_for_student(self, eval_id: int, email: str) -> str | None: ...

    @abstractmethod
    def get_peers_for_student(self, eval_id: int, email: str) -> list[Peer]: ...

    @abstractmethod
    def save_responses(
        self,
        eval_id: int,
        evaluator_student_id: int,
        evaluated_member_id: int,
        scores: dict[str, int],
    ) -> None: ...

    @abstractmethod
    def has_evaluated(
        self,
        eval_id: int,
        evaluator_student_id: int,
        evaluated_member_id: int,
    ) -> bool: ...

    @abstractmethod
    def has_completed_all_peers(
        self, eval_id: int, email: str, student_id: int
    ) -> bool: ...

    @abstractmethod
    def get_my_results(self, eval_id: int, email: str) -> list[CriterionResult]: ...

    @abstractmethod
    def get_group_results(self, eval_id: int) -> list[GroupResult]: ...
