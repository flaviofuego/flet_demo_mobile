from __future__ import annotations
from dataclasses import dataclass


@dataclass
class CourseModel:
    id: int
    teacher_id: int
    name: str
    code: str
    created_at: int  # epoch ms

    @staticmethod
    def from_row(row: dict) -> "CourseModel":
        return CourseModel(
            id=row["id"],
            teacher_id=row["teacher_id"],
            name=row["name"],
            code=row.get("code", ""),
            created_at=row["created_at"],
        )
