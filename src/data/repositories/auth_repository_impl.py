from __future__ import annotations
from src.data.services.database_service import DatabaseService
from src.data.utils import hash_password as _hash, build_initials as _build_initials
from src.domain.models.student import Student
from src.domain.repositories.i_auth_repository import IAuthRepository


class AuthRepositoryImpl(IAuthRepository):
    def __init__(self, db: DatabaseService) -> None:
        self._db = db

    def _conn(self):
        return self._db.connect()

    def _save_session(self, student_id: int) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM sessions")
        conn.execute(
            "INSERT INTO sessions (id, student_id) VALUES (1, ?)", (student_id,)
        )
        conn.commit()

    def login(self, email: str, password: str) -> Student | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT * FROM students WHERE email = ? AND password = ?",
            (email.strip().lower(), _hash(password)),
        ).fetchone()
        if row is None:
            return None
        self._save_session(row["id"])
        return Student.from_row(dict(row))

    def register(self, name: str, email: str, password: str) -> Student:
        conn = self._conn()
        initials = _build_initials(name)
        cursor = conn.execute(
            "INSERT INTO students (name, email, password, initials) VALUES (?,?,?,?)",
            (name.strip(), email.strip().lower(), _hash(password), initials),
        )
        conn.commit()
        self._save_session(cursor.lastrowid)
        return Student(
            id=str(cursor.lastrowid),
            name=name.strip(),
            email=email.strip().lower(),
            initials=initials,
        )

    def logout(self) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM sessions")
        conn.commit()

    def get_current_session(self) -> Student | None:
        conn = self._conn()
        session = conn.execute(
            "SELECT student_id FROM sessions WHERE id = 1"
        ).fetchone()
        if session is None:
            return None
        row = conn.execute(
            "SELECT * FROM students WHERE id = ?", (session["student_id"],)
        ).fetchone()
        if row is None:
            return None
        return Student.from_row(dict(row))
