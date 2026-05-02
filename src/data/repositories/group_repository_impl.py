from __future__ import annotations
import csv
import io
from datetime import datetime
from src.data.services.database_service import DatabaseService
from src.data.utils import hash_password as _hash, build_initials as _build_initials
from src.domain.models.group_category import GroupCategory, CourseGroup, GroupMember
from src.domain.repositories.i_group_repository import IGroupRepository


class GroupRepositoryImpl(IGroupRepository):
    def __init__(self, db: DatabaseService) -> None:
        self._db = db

    def _conn(self):
        return self._db.connect()

    def get_all(self, teacher_id: int) -> list[GroupCategory]:
        conn = self._conn()
        cat_rows = conn.execute(
            "SELECT * FROM group_categories WHERE teacher_id = ? ORDER BY imported_at DESC",
            (teacher_id,),
        ).fetchall()
        result = []
        for cat in cat_rows:
            cat_id = cat["id"]
            grp_rows = conn.execute(
                "SELECT * FROM groups WHERE category_id = ? ORDER BY name ASC",
                (cat_id,),
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
                    course_id=cat["course_id"] or 0,
                    groups=groups,
                )
            )
        return result

    def import_csv(
        self,
        csv_content: str,
        category_name: str,
        teacher_id: int,
        course_id: int,
    ) -> GroupCategory:
        """Parse Brightspace CSV format (7+ columns):
        col[1]=group name, col[3]=username/email, col[5]=first name, col[6]=last name
        """
        content = csv_content.lstrip("\ufeff")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        if not rows:
            raise ValueError("CSV vacío")
        data_rows = rows[1:]  # skip header
        group_map: dict[str, list[tuple[str, str]]] = {}
        for cols in data_rows:
            if len(cols) < 7:
                continue
            grp_name = cols[1].strip()
            username = cols[3].strip()
            first = cols[5].strip()
            last = cols[6].strip()
            name = f"{first} {last}".strip()
            if grp_name and username:
                group_map.setdefault(grp_name, []).append((name, username))
        if not group_map:
            raise ValueError("Sin datos de grupos válidos en el CSV")
        conn = self._conn()
        now_ms = int(datetime.now().timestamp() * 1000)
        cursor = conn.execute(
            "INSERT INTO group_categories (name, imported_at, teacher_id, course_id) VALUES (?,?,?,?)",
            (category_name, now_ms, teacher_id, course_id),
        )
        cat_id = cursor.lastrowid
        groups = []
        default_pw_hash = _hash("evalun2026")
        for grp_name, members_raw in group_map.items():
            grp_cursor = conn.execute(
                "INSERT INTO groups (category_id, name) VALUES (?,?)",
                (cat_id, grp_name),
            )
            grp_id = grp_cursor.lastrowid
            members = []
            for name, username in members_raw:
                mem_cursor = conn.execute(
                    "INSERT INTO group_members (group_id, name, username) VALUES (?,?,?)",
                    (grp_id, name, username),
                )
                mem_id = mem_cursor.lastrowid
                conn.execute(
                    "INSERT OR IGNORE INTO students (name, email, password, initials) VALUES (?,?,?,?)",
                    (name, username.lower(), default_pw_hash, _build_initials(name)),
                )
                members.append(GroupMember(id=mem_id, name=name, username=username))
            groups.append(CourseGroup(id=grp_id, name=grp_name, members=members))
        conn.commit()
        return GroupCategory(
            id=cat_id,
            name=category_name,
            imported_at=datetime.fromtimestamp(now_ms / 1000),
            course_id=course_id,
            groups=groups,
        )

    def delete(self, category_id: int) -> None:
        conn = self._conn()
        grp_rows = conn.execute(
            "SELECT id FROM groups WHERE category_id = ?", (category_id,)
        ).fetchall()
        for grp in grp_rows:
            conn.execute("DELETE FROM group_members WHERE group_id = ?", (grp["id"],))
        conn.execute("DELETE FROM groups WHERE category_id = ?", (category_id,))
        conn.execute("DELETE FROM group_categories WHERE id = ?", (category_id,))
        conn.commit()
