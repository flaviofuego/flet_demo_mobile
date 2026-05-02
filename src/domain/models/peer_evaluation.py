from __future__ import annotations
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class Peer:
    id: str
    name: str
    initials: str
    evaluated: bool = False
    scores: dict[str, int] = field(default_factory=dict)  # criterion_id → 2..5


# Module-level constant defined before class so it can be used as default
_LEVEL_LABELS: tuple[str, ...] = ("Necesita Mejorar", "Adecuado", "Bueno", "Excelente")


@dataclass
class EvalCriterion:
    id: str
    label: str

    DEFAULTS: ClassVar[list["EvalCriterion"]]

    @staticmethod
    def level_for(score: int) -> str:
        return _LEVEL_LABELS[score - 2]


EvalCriterion.DEFAULTS = [
    EvalCriterion(id="punct",    label="Puntualidad"),
    EvalCriterion(id="contrib",  label="Contribuciones"),
    EvalCriterion(id="commit",   label="Compromiso"),
    EvalCriterion(id="attitude", label="Actitud"),
]


@dataclass(frozen=True)
class CriterionResult:
    label: str
    value: float

    @property
    def bar_fraction(self) -> float:
        return max(0.0, min(1.0, (self.value - 2) / 3))
