from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GroupMember:
    id: int
    name: str
    username: str


@dataclass
class CourseGroup:
    id: int
    name: str
    members: list[GroupMember] = field(default_factory=list)


@dataclass
class GroupCategory:
    id: int
    name: str
    imported_at: datetime
    course_id: int = 0
    groups: list[CourseGroup] = field(default_factory=list)

    @property
    def group_count(self) -> int:
        return len(self.groups)

    @property
    def member_count(self) -> int:
        return sum(len(g.members) for g in self.groups)
