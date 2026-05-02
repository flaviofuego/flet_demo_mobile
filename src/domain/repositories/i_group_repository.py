from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.models.group_category import GroupCategory


class IGroupRepository(ABC):

    @abstractmethod
    def get_all(self, teacher_id: int) -> list[GroupCategory]: ...

    @abstractmethod
    def import_csv(
        self,
        csv_content: str,
        category_name: str,
        teacher_id: int,
        course_id: int,
    ) -> GroupCategory: ...

    @abstractmethod
    def delete(self, category_id: int) -> None: ...
