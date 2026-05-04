"""Local SQLite persistence — schema version 6, matching peerUn Flutter app."""
from __future__ import annotations

import os
import sqlite3


_DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".evalun", "peereval.db")


class DatabaseService:
    """Opens and maintains a SQLite connection with the peerUn v6 schema.

    Args:
        db_path: Path to the database file. Override in tests with a tmp_path.
    """

    def __init__(self, db_path: str = _DEFAULT_PATH) -> None:
        self._path = db_path
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """Return the connection, opening and migrating if necessary."""
        if self._conn is not None:
            return self._conn
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        conn = sqlite3.connect(self._path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        self._run_migrations(conn)
        self._conn = conn
        return conn

    # ------------------------------------------------------------------
    # Migrations
    # ------------------------------------------------------------------

    def _run_migrations(self, conn: sqlite3.Connection) -> None:
        user_version = conn.execute("PRAGMA user_version").fetchone()[0]

        if user_version < 1:
            self._create_v1(conn)
        if user_version < 2:
            self._create_v2(conn)
        if user_version < 3:
            self._create_v3(conn)
        if user_version < 4:
            self._create_v4(conn)
        if user_version < 5:
            self._upgrade_v5(conn)
        if user_version < 6:
            self._upgrade_v6(conn)
        if user_version < 7:
            self._upgrade_v7(conn)

        conn.execute("PRAGMA user_version = 7")
        conn.commit()

    @staticmethod
    def _create_v1(conn: sqlite3.Connection) -> None:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS students (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT    NOT NULL,
                email    TEXT    NOT NULL UNIQUE,
                password TEXT    NOT NULL,
                initials TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id         INTEGER PRIMARY KEY,
                student_id INTEGER,
                FOREIGN KEY (student_id) REFERENCES students(id)
            );
        """)

    @staticmethod
    def _create_v2(conn: sqlite3.Connection) -> None:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS teachers (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT    NOT NULL,
                email    TEXT    NOT NULL UNIQUE,
                password TEXT    NOT NULL,
                initials TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS teacher_sessions (
                id         INTEGER PRIMARY KEY,
                teacher_id INTEGER,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id)
            );
        """)

    @staticmethod
    def _create_v3(conn: sqlite3.Connection) -> None:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS group_categories (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                imported_at INTEGER NOT NULL,
                teacher_id  INTEGER NOT NULL DEFAULT 0,
                course_id   INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS groups (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name        TEXT    NOT NULL,
                FOREIGN KEY (category_id) REFERENCES group_categories(id)
            );
            CREATE TABLE IF NOT EXISTS group_members (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                name     TEXT    NOT NULL,
                username TEXT    NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups(id)
            );
        """)

    @staticmethod
    def _create_v4(conn: sqlite3.Connection) -> None:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                category_id INTEGER NOT NULL,
                hours       INTEGER NOT NULL,
                visibility  TEXT    NOT NULL,
                created_at  INTEGER NOT NULL,
                closes_at   INTEGER NOT NULL,
                teacher_id  INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (category_id) REFERENCES group_categories(id)
            );
            CREATE TABLE IF NOT EXISTS evaluation_responses (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                eval_id             INTEGER NOT NULL,
                evaluator_id        INTEGER NOT NULL,
                evaluated_member_id INTEGER NOT NULL,
                criterion_id        TEXT    NOT NULL,
                score               INTEGER NOT NULL,
                FOREIGN KEY (eval_id) REFERENCES evaluations(id)
            );
        """)

    @staticmethod
    def _upgrade_v5(conn: sqlite3.Connection) -> None:
        for stmt in [
            "ALTER TABLE group_categories ADD COLUMN teacher_id INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE evaluations ADD COLUMN teacher_id INTEGER NOT NULL DEFAULT 0",
        ]:
            try:
                conn.execute(stmt)
            except sqlite3.OperationalError:
                pass  # column already exists

    @staticmethod
    def _upgrade_v7(conn: sqlite3.Connection) -> None:
        try:
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_eval_response "
                "ON evaluation_responses(eval_id, evaluator_id, evaluated_member_id, criterion_id)"
            )
        except sqlite3.OperationalError:
            pass

    @staticmethod
    def _upgrade_v6(conn: sqlite3.Connection) -> None:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS courses (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL DEFAULT 0,
                name       TEXT    NOT NULL,
                code       TEXT    NOT NULL DEFAULT '',
                created_at INTEGER NOT NULL
            );
        """)
        try:
            conn.execute(
                "ALTER TABLE group_categories ADD COLUMN course_id INTEGER NOT NULL DEFAULT 0"
            )
        except sqlite3.OperationalError:
            pass
