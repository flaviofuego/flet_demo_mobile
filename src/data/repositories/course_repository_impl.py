from __future__ import annotations
from datetime import datetime
from src.data.services.database_service import DatabaseService
from src.domain.models.course import CourseModel
from src.domain.models.group_category import GroupCategory, CourseGroup, GroupMember
from src.domain.repositories.i_course_repository import ICourseRepository


class CourseRepositoryImpl(ICourseRepository):
    def __init__(self, db: DatabaseService) -> None:
        self._db = db

    def _conn(self):
        return self._db.connect()

    def get_all(self, teacher_id: int) -> list[CourseModel]:
        rows = self._conn().execute(
            "SELECT * FROM courses WHERE teacher_id = ? ORDER BY created_at DESC",
            (teacher_id,),
        ).fetchall()
        return [CourseModel.from_row(dict(r)) for r in rows]

    def create(self, name: str, code: str, teacher_id: int) -> CourseModel:
        conn = self._conn()
        now_ms = int(datetime.now().timestamp() * 1000)
        cursor = conn.execute(
            "INSERT INTO courses (teacher_id, name, code, created_at) VALUES (?,?,?,?)",
            (teacher_id, name.strip(), code.strip(), now_ms),
        )
        conn.commit()
        return CourseModel(
            id=cursor.lastrowid,
            teacher_id=teacher_id,
            name=name.strip(),
            code=code.strip(),
            created_at=now_ms,
        )

    def delete(self, course_id: int) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        conn.commit()

    def get_categories_for_course(self, course_id: int) -> list[GroupCategory]:
        conn = self._conn()
        cat_rows = conn.execute(
            "SELECT * FROM group_categories WHERE course_id = ? ORDER BY imported_at DESC",
            (course_id,),
        ).fetchall()
        result = []
        for cat in cat_rows:
            cat_id = cat["id"]
            grp_rows = conn.execute(
                "SELECT * FROM groups WHERE category_id = ?", (cat_id,)
            ).fetchall()
            groups = []
            for grp in grp_rows:
                grp_id = grp["id"]
                mem_rows = conn.execute(
                    "SELECT * FROM group_members WHERE group_id = ?", (grp_id,)
                ).fetchall()
                members = [
                    GroupMember(id=m["id"], name=m["name"], username=m["username"])
                    for m in mem_rows
                ]
                groups.append(CourseGroup(id=grp_id, name=grp["name"], members=members))
            result.append(
                GroupCategory(
                    id=cat_id,
                    name=cat["name"],
                    imported_at=datetime.fromtimestamp(cat["imported_at"] / 1000),
                    course_id=course_id,
                    groups=groups,
                )
            )
        return result
