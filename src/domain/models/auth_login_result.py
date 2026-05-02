from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class AppUserRole(Enum):
    student = "student"
    teacher = "teacher"


@dataclass
class AuthLoginResult:
    role: AppUserRole

    @property
    def home_route(self) -> str:
        return "/teacher/dash" if self.role == AppUserRole.teacher else "/student/courses"
