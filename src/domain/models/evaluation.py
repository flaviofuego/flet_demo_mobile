from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Evaluation:
    id: int
    name: str
    category_id: int
    category_name: str
    hours: int
    visibility: str          # 'public' | 'private'
    created_at: datetime
    closes_at: datetime
    course_name: str = ""    # denormalizado para display

    @property
    def is_active(self) -> bool:
        return datetime.now() < self.closes_at
