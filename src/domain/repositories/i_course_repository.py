from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.models.course import CourseModel
from src.domain.models.group_category import GroupCategory


class ICourseRepository(ABC):

    @abstractmethod
    def get_all(self, teacher_id: int) -> list[CourseModel]: ...

    @abstractmethod
    def create(self, name: str, code: str, teacher_id: int) -> CourseModel: ...

    @abstractmethod
    def delete(self, course_id: int) -> None: ...

    @abstractmethod
    def get_categories_for_course(self, course_id: int) -> list[GroupCategory]: ...
