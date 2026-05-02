from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Student:
    id: str
    name: str
    email: str
    initials: str

    @staticmethod
    def from_row(row: dict) -> "Student":
        return Student(
            id=str(row["id"]),
            name=row["name"],
            email=row["email"],
            initials=row["initials"],
        )
