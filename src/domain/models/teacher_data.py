from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class StudentResult:
    initial: str
    name: str
    score: float


@dataclass
class GroupResult:
    name: str
    average: float
    criteria: list[float] = field(default_factory=list)  # [punct, contrib, commit, attitude]
    students: list[StudentResult] = field(default_factory=list)
