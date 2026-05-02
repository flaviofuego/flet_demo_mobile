from __future__ import annotations
from src.data.services.database_service import DatabaseService
from src.data.utils import hash_password as _hash, build_initials as _build_initials
from src.domain.models.teacher import Teacher
from src.domain.repositories.i_teacher_auth_repository import ITeacherAuthRepository


class TeacherAuthRepositoryImpl(ITeacherAuthRepository):
    def __init__(self, db: DatabaseService) -> None:
        self._db = db

    def _conn(self):
        return self._db.connect()

    def _save_session(self, teacher_id: int) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM teacher_sessions")
        conn.execute(
            "INSERT INTO teacher_sessions (id, teacher_id) VALUES (1, ?)", (teacher_id,)
        )
        conn.commit()

    def login(self, email: str, password: str) -> Teacher | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT * FROM teachers WHERE email = ? AND password = ?",
            (email.strip().lower(), _hash(password)),
        ).fetchone()
        if row is None:
            return None
        self._save_session(row["id"])
        return Teacher.from_row(dict(row))

    def register(self, name: str, email: str, password: str) -> Teacher:
        conn = self._conn()
        initials = _build_initials(name)
        cursor = conn.execute(
            "INSERT INTO teachers (name, email, password, initials) VALUES (?,?,?,?)",
            (name.strip(), email.strip().lower(), _hash(password), initials),
        )
        conn.commit()
        self._save_session(cursor.lastrowid)
        return Teacher(
            id=str(cursor.lastrowid),
            name=name.strip(),
            email=email.strip().lower(),
            initials=initials,
        )

    def logout(self) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM teacher_sessions")
        conn.commit()

    def get_current_session(self) -> Teacher | None:
        conn = self._conn()
        session = conn.execute(
            "SELECT teacher_id FROM teacher_sessions WHERE id = 1"
        ).fetchone()
        if session is None:
            return None
        row = conn.execute(
            "SELECT * FROM teachers WHERE id = ?", (session["teacher_id"],)
        ).fetchone()
        if row is None:
            return None
        return Teacher.from_row(dict(row))
