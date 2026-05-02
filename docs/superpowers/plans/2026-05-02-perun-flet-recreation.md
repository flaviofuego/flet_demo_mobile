# peerUn → Flet Recreation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recrear la aplicación peerUn (EvalUn/Evalia) — evaluación entre pares, roles duales estudiante/docente, SQLite local, importación CSV Brightspace — completamente en Python/Flet manteniendo clean architecture.

**Architecture:** Mismas tres capas que el repo demo: dominio (modelos + interfaces de repositorios), datos (SQLite con `sqlite3` stdlib + implementaciones), presentación (Flet Views + ViewModels con callback `_notify`). Navegación vía `page.views` / `page.on_route_change`. No se usa estado reactivo externo: los ViewModels llaman `_notify()` → `page.update()`.

**Tech Stack:** Python 3.11+, Flet ≥ 0.23.0, `sqlite3` (stdlib), `hashlib` SHA-256 (stdlib), `csv` (stdlib), `dataclasses`, `pytest`, `pytest-cov`.

---

## Mapa de archivos

### Eliminar (reemplazados por peerUn)
- `src/domain/entities/user.py`
- `src/domain/repositories/user_repository.py`
- `src/domain/usecases/get_users.py`
- `src/data/models/user_model.py`
- `src/data/datasources/user_local_datasource.py`
- `src/data/repositories/user_repository_impl.py`
- `src/presentation/pages/home_page.py`
- `src/presentation/components/user_card.py`
- `src/presentation/viewmodels/home_viewmodel.py`

### Conservar sin cambios
- `src/core/error/exceptions.py`
- `src/core/utils/result.py`
- `pyproject.toml` (solo ajustar nombre del proyecto)
- `requirements.txt`

### Crear nuevos

**Datos:**
- `src/data/services/database_service.py`
- `src/data/repositories/auth_repository_impl.py`
- `src/data/repositories/teacher_auth_repository_impl.py`
- `src/data/repositories/unified_auth_repository_impl.py`
- `src/data/repositories/group_repository_impl.py`
- `src/data/repositories/course_repository_impl.py`
- `src/data/repositories/evaluation_repository_impl.py`

**Dominio:**
- `src/domain/models/student.py`
- `src/domain/models/teacher.py`
- `src/domain/models/course.py`
- `src/domain/models/evaluation.py`
- `src/domain/models/peer_evaluation.py`
- `src/domain/models/auth_login_result.py`
- `src/domain/models/group_category.py`
- `src/domain/models/teacher_data.py`
- `src/domain/repositories/i_auth_repository.py`
- `src/domain/repositories/i_teacher_auth_repository.py`
- `src/domain/repositories/i_unified_auth_repository.py`
- `src/domain/repositories/i_group_repository.py`
- `src/domain/repositories/i_course_repository.py`
- `src/domain/repositories/i_evaluation_repository.py`

**Presentación:**
- `src/presentation/theme/app_colors.py`
- `src/presentation/viewmodels/login_viewmodel.py`
- `src/presentation/viewmodels/student_viewmodel.py`
- `src/presentation/viewmodels/teacher_viewmodel.py`
- `src/presentation/pages/auth/login_page.py`
- `src/presentation/pages/auth/register_page.py`
- `src/presentation/pages/student/s_courses_page.py`
- `src/presentation/pages/student/s_eval_list_page.py`
- `src/presentation/pages/student/s_peers_page.py`
- `src/presentation/pages/student/s_peer_score_page.py`
- `src/presentation/pages/student/s_my_results_page.py`
- `src/presentation/pages/teacher/t_dash_page.py`
- `src/presentation/pages/teacher/t_import_page.py`
- `src/presentation/pages/teacher/t_new_eval_page.py`
- `src/presentation/pages/teacher/t_results_page.py`
- `src/presentation/pages/teacher/t_profile_page.py`
- `src/presentation/pages/teacher/t_course_manage_page.py`
- `src/presentation/components/avatar_circle.py`

**Tests:**
- `tests/domain/test_domain_models.py`
- `tests/data/test_database_service.py`
- `tests/presentation/test_student_viewmodel.py`

### Modificar
- `main.py` — reescribir DI + router + splash

---

## Task 1: Domain Models

**Files:**
- Create: `src/domain/models/student.py`
- Create: `src/domain/models/teacher.py`
- Create: `src/domain/models/course.py`
- Create: `src/domain/models/evaluation.py`
- Create: `src/domain/models/peer_evaluation.py`
- Create: `src/domain/models/auth_login_result.py`
- Create: `src/domain/models/group_category.py`
- Create: `src/domain/models/teacher_data.py`
- Test: `tests/domain/test_domain_models.py`

- [ ] **Step 1: Escribir tests fallidos para modelos de dominio**

```python
# tests/domain/test_domain_models.py
from datetime import datetime, timedelta
from src.domain.models.evaluation import Evaluation
from src.domain.models.peer_evaluation import EvalCriterion, CriterionResult, Peer


def test_evaluation_is_active_when_closes_in_future():
    now = datetime.now()
    ev = Evaluation(
        id=1, name="Sprint 1", category_id=1, category_name="Grupo A",
        hours=48, visibility="public",
        created_at=now, closes_at=now + timedelta(hours=48),
    )
    assert ev.is_active is True


def test_evaluation_is_inactive_when_closed():
    past = datetime.now() - timedelta(hours=1)
    ev = Evaluation(
        id=1, name="Sprint 1", category_id=1, category_name="Grupo A",
        hours=48, visibility="private",
        created_at=past - timedelta(hours=48), closes_at=past,
    )
    assert ev.is_active is False


def test_criterion_level_for_scores():
    assert EvalCriterion.level_for(2) == "Necesita Mejorar"
    assert EvalCriterion.level_for(3) == "Adecuado"
    assert EvalCriterion.level_for(4) == "Bueno"
    assert EvalCriterion.level_for(5) == "Excelente"


def test_criterion_result_bar_fraction():
    r = CriterionResult(label="Puntualidad", value=2.0)
    assert r.bar_fraction == 0.0
    r5 = CriterionResult(label="Puntualidad", value=5.0)
    assert r5.bar_fraction == 1.0
    r35 = CriterionResult(label="Puntualidad", value=3.5)
    assert abs(r35.bar_fraction - 0.5) < 0.01


def test_peer_default_scores_empty():
    p = Peer(id="1", name="Ana López", initials="AL")
    assert p.scores == {}
    assert p.evaluated is False
```

- [ ] **Step 2: Ejecutar tests para verificar que fallan**

```bash
pytest tests/domain/test_domain_models.py -v
```
Expected: `ModuleNotFoundError` o `ImportError`

- [ ] **Step 3: Crear modelos de dominio**

```python
# src/domain/models/student.py
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
```

```python
# src/domain/models/teacher.py
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Teacher:
    id: str
    name: str
    email: str
    initials: str

    @staticmethod
    def from_row(row: dict) -> "Teacher":
        return Teacher(
            id=str(row["id"]),
            name=row["name"],
            email=row["email"],
            initials=row["initials"],
        )
```

```python
# src/domain/models/evaluation.py
from __future__ import annotations
from dataclasses import dataclass, field
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
```

```python
# src/domain/models/peer_evaluation.py
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Peer:
    id: str
    name: str
    initials: str
    evaluated: bool = False
    scores: dict[str, int] = field(default_factory=dict)  # criterion_id → 2..5


@dataclass(frozen=True)
class EvalCriterion:
    id: str
    label: str

    DEFAULTS: list["EvalCriterion"]  # se asigna después de la clase

    _LEVEL_LABELS = ("Necesita Mejorar", "Adecuado", "Bueno", "Excelente")

    @staticmethod
    def level_for(score: int) -> str:
        return EvalCriterion._LEVEL_LABELS[score - 2]


EvalCriterion.DEFAULTS = [
    EvalCriterion(id="punct",    label="Puntualidad",     DEFAULTS=None),
    EvalCriterion(id="contrib",  label="Contribuciones",  DEFAULTS=None),
    EvalCriterion(id="commit",   label="Compromiso",      DEFAULTS=None),
    EvalCriterion(id="attitude", label="Actitud",         DEFAULTS=None),
]


@dataclass(frozen=True)
class CriterionResult:
    label: str
    value: float

    @property
    def bar_fraction(self) -> float:
        return max(0.0, min(1.0, (self.value - 2) / 3))
```

> **Nota:** `EvalCriterion` tiene un campo `DEFAULTS` para permitir `frozen=True` sin mutabilidad de clase. Si esto genera linter errors, alternativa es usar `ClassVar`:

```python
# Alternativa limpia para EvalCriterion
from __future__ import annotations
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class EvalCriterion:
    id: str
    label: str

    DEFAULTS: ClassVar[list["EvalCriterion"]] = []
    _LEVEL_LABELS: ClassVar[tuple[str, ...]] = (
        "Necesita Mejorar", "Adecuado", "Bueno", "Excelente"
    )

    @staticmethod
    def level_for(score: int) -> str:
        return EvalCriterion._LEVEL_LABELS[score - 2]


EvalCriterion.DEFAULTS = [
    EvalCriterion(id="punct",    label="Puntualidad"),
    EvalCriterion(id="contrib",  label="Contribuciones"),
    EvalCriterion(id="commit",   label="Compromiso"),
    EvalCriterion(id="attitude", label="Actitud"),
]
```

```python
# src/domain/models/auth_login_result.py
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class AppUserRole(Enum):
    student = "student"
    teacher = "teacher"


@dataclass
class AuthLoginResult:
    role: AppUserRole

    @property
    def home_route(self) -> str:
        return "/teacher/dash" if self.role == AppUserRole.teacher else "/student/courses"
```

```python
# src/domain/models/group_category.py
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GroupMember:
    id: int
    name: str
    username: str


@dataclass
class CourseGroup:
    id: int
    name: str
    members: list[GroupMember] = field(default_factory=list)


@dataclass
class GroupCategory:
    id: int
    name: str
    imported_at: datetime
    course_id: int = 0
    groups: list[CourseGroup] = field(default_factory=list)

    @property
    def group_count(self) -> int:
        return len(self.groups)

    @property
    def member_count(self) -> int:
        return sum(len(g.members) for g in self.groups)
```

```python
# src/domain/models/course.py
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
```

```python
# src/domain/models/teacher_data.py
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class StudentResult:
    initial: str
    name: str
    score: float


@dataclass
class GroupResult:
    name: str
    average: float
    criteria: list[float] = field(default_factory=list)  # [punct, contrib, commit, attitude]
    students: list[StudentResult] = field(default_factory=list)
```

- [ ] **Step 4: Crear `__init__.py` en `src/domain/models/`**

```python
# src/domain/models/__init__.py
```

- [ ] **Step 5: Ejecutar tests y verificar que pasan**

```bash
pytest tests/domain/test_domain_models.py -v
```
Expected: todos PASS

- [ ] **Step 6: Commit**

```bash
git add src/domain/models/ tests/domain/test_domain_models.py
git commit -m "feat: add peerUn domain models"
```

---

## Task 2: Repository Interfaces (Dominio)

**Files:**
- Create: `src/domain/repositories/i_auth_repository.py`
- Create: `src/domain/repositories/i_teacher_auth_repository.py`
- Create: `src/domain/repositories/i_unified_auth_repository.py`
- Create: `src/domain/repositories/i_group_repository.py`
- Create: `src/domain/repositories/i_course_repository.py`
- Create: `src/domain/repositories/i_evaluation_repository.py`

- [ ] **Step 1: Crear interfaces usando ABC**

```python
# src/domain/repositories/i_auth_repository.py
from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.models.student import Student


class IAuthRepository(ABC):

    @abstractmethod
    def login(self, email: str, password: str) -> Student | None: ...

    @abstractmethod
    def register(self, name: str, email: str, password: str) -> Student: ...

    @abstractmethod
    def logout(self) -> None: ...

    @abstractmethod
    def get_current_session(self) -> Student | None: ...
```

```python
# src/domain/repositories/i_teacher_auth_repository.py
from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.models.teacher import Teacher


class ITeacherAuthRepository(ABC):

    @abstractmethod
    def login(self, email: str, password: str) -> Teacher | None: ...

    @abstractmethod
    def register(self, name: str, email: str, password: str) -> Teacher: ...

    @abstractmethod
    def logout(self) -> None: ...

    @abstractmethod
    def get_current_session(self) -> Teacher | None: ...
```

```python
# src/domain/repositories/i_unified_auth_repository.py
from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.models.auth_login_result import AuthLoginResult


class IUnifiedAuthRepository(ABC):

    @abstractmethod
    def login_and_resolve(self, email: str, password: str) -> AuthLoginResult | None: ...
```

```python
# src/domain/repositories/i_group_repository.py
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
```

```python
# src/domain/repositories/i_course_repository.py
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
```

```python
# src/domain/repositories/i_evaluation_repository.py
from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.models.evaluation import Evaluation
from src.domain.models.peer_evaluation import Peer, CriterionResult
from src.domain.models.teacher_data import GroupResult


class IEvaluationRepository(ABC):

    @abstractmethod
    def create(
        self,
        name: str,
        category_id: int,
        hours: int,
        visibility: str,
        teacher_id: int,
    ) -> Evaluation: ...

    @abstractmethod
    def get_all(self, teacher_id: int) -> list[Evaluation]: ...

    @abstractmethod
    def rename(self, eval_id: int, new_name: str, teacher_id: int) -> None: ...

    @abstractmethod
    def delete(self, eval_id: int) -> None: ...

    @abstractmethod
    def get_evaluations_for_student(self, email: str) -> list[Evaluation]: ...

    @abstractmethod
    def get_group_name_for_student(self, eval_id: int, email: str) -> str | None: ...

    @abstractmethod
    def get_peers_for_student(self, eval_id: int, email: str) -> list[Peer]: ...

    @abstractmethod
    def save_responses(
        self,
        eval_id: int,
        evaluator_student_id: int,
        evaluated_member_id: int,
        scores: dict[str, int],
    ) -> None: ...

    @abstractmethod
    def has_evaluated(
        self,
        eval_id: int,
        evaluator_student_id: int,
        evaluated_member_id: int,
    ) -> bool: ...

    @abstractmethod
    def has_completed_all_peers(
        self, eval_id: int, email: str, student_id: int
    ) -> bool: ...

    @abstractmethod
    def get_my_results(self, eval_id: int, email: str) -> list[CriterionResult]: ...

    @abstractmethod
    def get_group_results(self, eval_id: int) -> list[GroupResult]: ...
```

- [ ] **Step 2: Commit**

```bash
git add src/domain/repositories/
git commit -m "feat: add peerUn repository interfaces"
```

---

## Task 3: Database Service

**Files:**
- Create: `src/data/services/database_service.py`
- Create: `src/data/services/__init__.py`
- Test: `tests/data/test_database_service.py`

- [ ] **Step 1: Escribir tests de database service**

```python
# tests/data/test_database_service.py
import sqlite3
import pytest
from src.data.services.database_service import DatabaseService


@pytest.fixture
def db_service(tmp_path):
    """DatabaseService apuntando a DB en memoria (tmp_path/test.db)."""
    svc = DatabaseService(db_path=str(tmp_path / "test.db"))
    return svc


def test_database_creates_all_tables(db_service):
    db = db_service.connect()
    cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    expected = {
        "students", "sessions", "teachers", "teacher_sessions",
        "courses", "group_categories", "groups", "group_members",
        "evaluations", "evaluation_responses",
    }
    assert expected.issubset(tables)


def test_connect_returns_same_connection(db_service):
    c1 = db_service.connect()
    c2 = db_service.connect()
    assert c1 is c2


def test_students_table_has_unique_email(db_service):
    db = db_service.connect()
    db.execute(
        "INSERT INTO students (name, email, password, initials) VALUES (?,?,?,?)",
        ("Ana", "ana@uni.edu", "hash", "A"),
    )
    db.commit()
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO students (name, email, password, initials) VALUES (?,?,?,?)",
            ("Ana2", "ana@uni.edu", "hash2", "A2"),
        )
```

- [ ] **Step 2: Verificar que fallan**

```bash
pytest tests/data/test_database_service.py -v
```
Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implementar DatabaseService**

```python
# src/data/services/__init__.py
```

```python
# src/data/services/database_service.py
"""Local SQLite persistence — schema version 6."""
from __future__ import annotations

import sqlite3
import os


_DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".evalun", "peereval.db")


class DatabaseService:
    """Abre y mantiene una conexión SQLite con el esquema v6 de peerUn.

    Args:
        db_path: Ruta al archivo de base de datos.  Se puede sobreescribir
                 en tests para usar un directorio temporal.
    """

    def __init__(self, db_path: str = _DEFAULT_PATH) -> None:
        self._path = db_path
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """Devuelve la conexión, abriéndola y migrando si es necesario."""
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

        conn.execute("PRAGMA user_version = 6")
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
```

- [ ] **Step 4: Ejecutar tests**

```bash
pytest tests/data/test_database_service.py -v
```
Expected: todos PASS

- [ ] **Step 5: Commit**

```bash
git add src/data/services/ tests/data/test_database_service.py
git commit -m "feat: add SQLite database service with schema v6"
```

---

## Task 4: Auth Repositories

**Files:**
- Create: `src/data/repositories/auth_repository_impl.py`
- Create: `src/data/repositories/teacher_auth_repository_impl.py`
- Create: `src/data/repositories/unified_auth_repository_impl.py`

- [ ] **Step 1: Implementar helpers compartidos y AuthRepositoryImpl**

```python
# src/data/repositories/auth_repository_impl.py
from __future__ import annotations

import hashlib

from src.data.services.database_service import DatabaseService
from src.domain.models.student import Student
from src.domain.repositories.i_auth_repository import IAuthRepository


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _build_initials(name: str) -> str:
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


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
```

```python
# src/data/repositories/teacher_auth_repository_impl.py
from __future__ import annotations

import hashlib

from src.data.services.database_service import DatabaseService
from src.domain.models.teacher import Teacher
from src.domain.repositories.i_teacher_auth_repository import ITeacherAuthRepository


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _build_initials(name: str) -> str:
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


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
```

```python
# src/data/repositories/unified_auth_repository_impl.py
from __future__ import annotations

from src.domain.models.auth_login_result import AuthLoginResult, AppUserRole
from src.domain.repositories.i_auth_repository import IAuthRepository
from src.domain.repositories.i_teacher_auth_repository import ITeacherAuthRepository
from src.domain.repositories.i_unified_auth_repository import IUnifiedAuthRepository


class UnifiedAuthRepositoryImpl(IUnifiedAuthRepository):
    """Intenta login como docente primero, luego como estudiante."""

    def __init__(
        self,
        student_auth: IAuthRepository,
        teacher_auth: ITeacherAuthRepository,
    ) -> None:
        self._student = student_auth
        self._teacher = teacher_auth

    def login_and_resolve(self, email: str, password: str) -> AuthLoginResult | None:
        teacher = self._teacher.login(email, password)
        if teacher is not None:
            self._student.logout()
            return AuthLoginResult(role=AppUserRole.teacher)

        student = self._student.login(email, password)
        if student is not None:
            self._teacher.logout()
            return AuthLoginResult(role=AppUserRole.student)

        return None
```

- [ ] **Step 2: Commit**

```bash
git add src/data/repositories/auth_repository_impl.py \
        src/data/repositories/teacher_auth_repository_impl.py \
        src/data/repositories/unified_auth_repository_impl.py
git commit -m "feat: auth repository impls (student, teacher, unified)"
```

---

## Task 5: Group Repository (CSV Import)

**Files:**
- Create: `src/data/repositories/group_repository_impl.py`

- [ ] **Step 1: Implementar GroupRepositoryImpl**

```python
# src/data/repositories/group_repository_impl.py
from __future__ import annotations

import csv
import hashlib
import io
from datetime import datetime

from src.data.services.database_service import DatabaseService
from src.domain.models.group_category import GroupCategory, CourseGroup, GroupMember
from src.domain.repositories.i_group_repository import IGroupRepository


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _build_initials(name: str) -> str:
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


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
                    GroupMember(
                        id=m["id"], name=m["name"], username=m["username"]
                    )
                    for m in mem_rows
                ]
                groups.append(
                    CourseGroup(id=grp_id, name=grp["name"], members=members)
                )
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
        """Parsea formato Brightspace (7+ columnas):
        col[1]=grupo, col[3]=username/email, col[5]=nombre, col[6]=apellido
        """
        # Strip UTF-8 BOM
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
        default_password_hash = _hash("evalun2026")

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
                # Register student with default password if not already present
                conn.execute(
                    """INSERT OR IGNORE INTO students (name, email, password, initials)
                       VALUES (?,?,?,?)""",
                    (name, username.lower(), default_password_hash, _build_initials(name)),
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
            conn.execute(
                "DELETE FROM group_members WHERE group_id = ?", (grp["id"],)
            )
        conn.execute("DELETE FROM groups WHERE category_id = ?", (category_id,))
        conn.execute("DELETE FROM group_categories WHERE id = ?", (category_id,))
        conn.commit()
```

- [ ] **Step 2: Commit**

```bash
git add src/data/repositories/group_repository_impl.py
git commit -m "feat: group repository with Brightspace CSV import"
```

---

## Task 6: Course Repository

**Files:**
- Create: `src/data/repositories/course_repository_impl.py`

- [ ] **Step 1: Implementar CourseRepositoryImpl**

```python
# src/data/repositories/course_repository_impl.py
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
```

- [ ] **Step 2: Commit**

```bash
git add src/data/repositories/course_repository_impl.py
git commit -m "feat: course repository impl"
```

---

## Task 7: Evaluation Repository

**Files:**
- Create: `src/data/repositories/evaluation_repository_impl.py`

- [ ] **Step 1: Implementar EvaluationRepositoryImpl**

```python
# src/data/repositories/evaluation_repository_impl.py
from __future__ import annotations

from datetime import datetime, timedelta

from src.data.services.database_service import DatabaseService
from src.domain.models.evaluation import Evaluation
from src.domain.models.peer_evaluation import Peer, CriterionResult, EvalCriterion
from src.domain.models.teacher_data import GroupResult, StudentResult
from src.domain.repositories.i_evaluation_repository import IEvaluationRepository


def _build_initials(name: str) -> str:
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _row_to_eval(row: dict) -> Evaluation:
    return Evaluation(
        id=row["id"],
        name=row["name"],
        category_id=row["category_id"],
        category_name=row["category_name"],
        course_name=row.get("course_name") or "",
        hours=row["hours"],
        visibility=row["visibility"],
        created_at=datetime.fromtimestamp(row["created_at"] / 1000),
        closes_at=datetime.fromtimestamp(row["closes_at"] / 1000),
    )


class EvaluationRepositoryImpl(IEvaluationRepository):
    def __init__(self, db: DatabaseService) -> None:
        self._db = db

    def _conn(self):
        return self._db.connect()

    # ── Create ─────────────────────────────────────────────────────────────────

    def create(
        self,
        name: str,
        category_id: int,
        hours: int,
        visibility: str,
        teacher_id: int,
    ) -> Evaluation:
        conn = self._conn()
        dup = conn.execute(
            "SELECT id FROM evaluations WHERE LOWER(name)=? AND teacher_id=?",
            (name.lower(), teacher_id),
        ).fetchone()
        if dup:
            raise ValueError("Ya existe una evaluación con ese nombre")
        now = datetime.now()
        closes = now + timedelta(hours=hours)
        now_ms = int(now.timestamp() * 1000)
        closes_ms = int(closes.timestamp() * 1000)
        cursor = conn.execute(
            """INSERT INTO evaluations
               (name, category_id, hours, visibility, created_at, closes_at, teacher_id)
               VALUES (?,?,?,?,?,?,?)""",
            (name, category_id, hours, visibility, now_ms, closes_ms, teacher_id),
        )
        conn.commit()
        eval_id = cursor.lastrowid
        cat_row = conn.execute(
            "SELECT name FROM group_categories WHERE id=?", (category_id,)
        ).fetchone()
        cat_name = cat_row["name"] if cat_row else ""
        return Evaluation(
            id=eval_id,
            name=name,
            category_id=category_id,
            category_name=cat_name,
            hours=hours,
            visibility=visibility,
            created_at=now,
            closes_at=closes,
        )

    # ── Read ───────────────────────────────────────────────────────────────────

    def get_all(self, teacher_id: int) -> list[Evaluation]:
        rows = self._conn().execute(
            """SELECT e.*, gc.name AS category_name, co.name AS course_name
               FROM evaluations e
               JOIN group_categories gc ON gc.id = e.category_id
               LEFT JOIN courses co     ON co.id = gc.course_id
               WHERE e.teacher_id = ?
               ORDER BY e.created_at DESC""",
            (teacher_id,),
        ).fetchall()
        return [_row_to_eval(dict(r)) for r in rows]

    def rename(self, eval_id: int, new_name: str, teacher_id: int) -> None:
        conn = self._conn()
        dup = conn.execute(
            "SELECT id FROM evaluations WHERE LOWER(name)=? AND teacher_id=? AND id!=?",
            (new_name.lower(), teacher_id, eval_id),
        ).fetchone()
        if dup:
            raise ValueError("Ya existe una evaluación con ese nombre")
        conn.execute(
            "UPDATE evaluations SET name=? WHERE id=?", (new_name, eval_id)
        )
        conn.commit()

    def delete(self, eval_id: int) -> None:
        conn = self._conn()
        conn.execute(
            "DELETE FROM evaluation_responses WHERE eval_id=?", (eval_id,)
        )
        conn.execute("DELETE FROM evaluations WHERE id=?", (eval_id,))
        conn.commit()

    # ── Student queries ────────────────────────────────────────────────────────

    def get_evaluations_for_student(self, email: str) -> list[Evaluation]:
        rows = self._conn().execute(
            """SELECT DISTINCT e.*, gc.name AS category_name, co.name AS course_name
               FROM evaluations e
               JOIN group_categories gc ON gc.id = e.category_id
               LEFT JOIN courses co     ON co.id = gc.course_id
               JOIN groups g            ON g.category_id = e.category_id
               JOIN group_members gm    ON gm.group_id = g.id
               WHERE LOWER(gm.username) = ?
               ORDER BY e.created_at DESC""",
            (email.lower(),),
        ).fetchall()
        return [_row_to_eval(dict(r)) for r in rows]

    def get_group_name_for_student(self, eval_id: int, email: str) -> str | None:
        row = self._conn().execute(
            """SELECT g.name FROM groups g
               JOIN group_members gm ON gm.group_id = g.id
               JOIN evaluations e    ON e.category_id = g.category_id
               WHERE e.id=? AND LOWER(gm.username)=?
               LIMIT 1""",
            (eval_id, email.lower()),
        ).fetchone()
        return row["name"] if row else None

    def get_peers_for_student(self, eval_id: int, email: str) -> list[Peer]:
        conn = self._conn()
        grp = conn.execute(
            """SELECT g.id FROM groups g
               JOIN group_members gm ON gm.group_id = g.id
               JOIN evaluations e    ON e.category_id = g.category_id
               WHERE e.id=? AND LOWER(gm.username)=?
               LIMIT 1""",
            (eval_id, email.lower()),
        ).fetchone()
        if grp is None:
            return []
        grp_id = grp["id"]
        rows = conn.execute(
            "SELECT * FROM group_members WHERE group_id=? AND LOWER(username)!=?",
            (grp_id, email.lower()),
        ).fetchall()
        return [
            Peer(
                id=str(m["id"]),
                name=m["name"],
                initials=_build_initials(m["name"]),
            )
            for m in rows
        ]

    # ── Responses ──────────────────────────────────────────────────────────────

    def save_responses(
        self,
        eval_id: int,
        evaluator_student_id: int,
        evaluated_member_id: int,
        scores: dict[str, int],
    ) -> None:
        conn = self._conn()
        for criterion_id, score in scores.items():
            conn.execute(
                """INSERT INTO evaluation_responses
                   (eval_id, evaluator_id, evaluated_member_id, criterion_id, score)
                   VALUES (?,?,?,?,?)""",
                (eval_id, evaluator_student_id, evaluated_member_id, criterion_id, score),
            )
        conn.commit()

    def has_evaluated(
        self,
        eval_id: int,
        evaluator_student_id: int,
        evaluated_member_id: int,
    ) -> bool:
        row = self._conn().execute(
            """SELECT 1 FROM evaluation_responses
               WHERE eval_id=? AND evaluator_id=? AND evaluated_member_id=?
               LIMIT 1""",
            (eval_id, evaluator_student_id, evaluated_member_id),
        ).fetchone()
        return row is not None

    def has_completed_all_peers(
        self, eval_id: int, email: str, student_id: int
    ) -> bool:
        conn = self._conn()
        grp = conn.execute(
            """SELECT g.id FROM groups g
               JOIN group_members gm ON gm.group_id = g.id
               JOIN evaluations e    ON e.category_id = g.category_id
               WHERE e.id=? AND LOWER(gm.username)=?
               LIMIT 1""",
            (eval_id, email.lower()),
        ).fetchone()
        if grp is None:
            return False
        grp_id = grp["id"]
        peer_rows = conn.execute(
            "SELECT id FROM group_members WHERE group_id=? AND LOWER(username)!=?",
            (grp_id, email.lower()),
        ).fetchall()
        total = len(peer_rows)
        if total == 0:
            return False
        peer_ids = [r["id"] for r in peer_rows]
        placeholders = ",".join("?" * len(peer_ids))
        done_row = conn.execute(
            f"""SELECT COUNT(DISTINCT evaluated_member_id) AS cnt
                FROM evaluation_responses
                WHERE eval_id=? AND evaluator_id=?
                AND evaluated_member_id IN ({placeholders})""",
            (eval_id, student_id, *peer_ids),
        ).fetchone()
        done = done_row["cnt"] if done_row else 0
        return done >= total

    def get_my_results(self, eval_id: int, email: str) -> list[CriterionResult]:
        conn = self._conn()
        member_rows = conn.execute(
            """SELECT gm.id FROM group_members gm
               JOIN groups g      ON g.id = gm.group_id
               JOIN evaluations e ON e.category_id = g.category_id
               WHERE e.id=? AND LOWER(gm.username)=?""",
            (eval_id, email.lower()),
        ).fetchall()
        if not member_rows:
            return []
        member_ids = [r["id"] for r in member_rows]
        placeholders = ",".join("?" * len(member_ids))
        rows = conn.execute(
            f"""SELECT criterion_id, AVG(CAST(score AS REAL)) AS avg_score
                FROM evaluation_responses
                WHERE eval_id=? AND evaluated_member_id IN ({placeholders}) AND score>=2
                GROUP BY criterion_id""",
            (eval_id, *member_ids),
        ).fetchall()
        avg_map = {r["criterion_id"]: r["avg_score"] for r in rows}
        return [
            CriterionResult(
                label=c.label,
                value=round(avg_map.get(c.id, 0.0), 1),
            )
            for c in EvalCriterion.DEFAULTS
        ]

    # ── Group results (teacher) ────────────────────────────────────────────────

    def get_group_results(self, eval_id: int) -> list[GroupResult]:
        conn = self._conn()
        member_rows = conn.execute(
            """SELECT g.id AS grp_id, g.name AS grp_name,
                      gm.id AS mem_id, gm.name AS mem_name,
                      COALESCE(
                          AVG(CASE WHEN er.score >= 2 THEN CAST(er.score AS REAL) END),
                          0.0
                      ) AS avg_score
               FROM groups g
               JOIN evaluations e    ON e.category_id = g.category_id
               JOIN group_members gm ON gm.group_id = g.id
               LEFT JOIN evaluation_responses er
                      ON er.eval_id = e.id
                     AND er.evaluated_member_id = gm.id
                     AND er.score >= 2
               WHERE e.id=?
               GROUP BY g.id, gm.id
               ORDER BY g.name, gm.name""",
            (eval_id,),
        ).fetchall()

        crit_rows = conn.execute(
            """SELECT g.id AS grp_id, er.criterion_id,
                      AVG(CAST(er.score AS REAL)) AS avg_score
               FROM groups g
               JOIN evaluations e    ON e.category_id = g.category_id
               JOIN group_members gm ON gm.group_id = g.id
               JOIN evaluation_responses er
                      ON er.eval_id = e.id
                     AND er.evaluated_member_id = gm.id
                     AND er.score >= 2
               WHERE e.id=?
               GROUP BY g.id, er.criterion_id""",
            (eval_id,),
        ).fetchall()

        # Build criterion map grp_id → {criterion_id → avg}
        crit_map: dict[int, dict[str, float]] = {}
        for r in crit_rows:
            crit_map.setdefault(r["grp_id"], {})[r["criterion_id"]] = r["avg_score"]

        # Group member rows by group id
        group_names: dict[int, str] = {}
        group_members: dict[int, list] = {}
        for r in member_rows:
            gid = r["grp_id"]
            group_names[gid] = r["grp_name"]
            group_members.setdefault(gid, []).append(r)

        CRITERION_IDS = ["punct", "contrib", "commit", "attitude"]
        results = []
        for gid, gname in group_names.items():
            members = group_members.get(gid, [])
            students = [
                StudentResult(
                    initial=(m["mem_name"][0].upper() if m["mem_name"] else "?"),
                    name=m["mem_name"],
                    score=round(m["avg_score"], 1),
                )
                for m in members
            ]
            cm = crit_map.get(gid, {})
            criteria = [round(cm.get(cid, 0.0), 1) for cid in CRITERION_IDS]
            valid = [s.score for s in students if s.score > 0]
            average = round(sum(valid) / len(valid), 1) if valid else 0.0
            results.append(
                GroupResult(
                    name=gname,
                    average=average,
                    criteria=criteria,
                    students=students,
                )
            )
        return results
```

- [ ] **Step 2: Commit**

```bash
git add src/data/repositories/evaluation_repository_impl.py
git commit -m "feat: evaluation repository impl (full CRUD + results)"
```

---

## Task 8: Theme

**Files:**
- Create: `src/presentation/theme/app_colors.py`
- Create: `src/presentation/theme/__init__.py`

- [ ] **Step 1: Crear paleta de colores SK (estudiante) y TK (docente)**

```python
# src/presentation/theme/__init__.py
```

```python
# src/presentation/theme/app_colors.py
"""Paleta de colores de EvalUn, portada desde app_colors.dart y teacher_colors.dart."""

# ── SK — Student Kit (modo claro) ─────────────────────────────────────────────
SK_BACKGROUND    = "#F8FAFB"
SK_SURFACE       = "#FFFFFF"
SK_SURFACE_ALT   = "#F3F2FA"
SK_BORDER        = "#E6E4F2"
SK_BORDER_MID    = "#CFCBE6"
SK_TEXT          = "#2B2540"
SK_TEXT_MID      = "#5E5A7A"
SK_TEXT_FAINT    = "#A3A0C2"
SK_PRIMARY       = "#7C83D6"
SK_PRIMARY_MID   = "#6A72C9"
SK_PRIMARY_LIGHT = "#EEEFFE"

# Colores de criterio (modo claro)
CRIT_BLUE   = "#0EA5E9"
CRIT_PURPLE = "#8B5CF6"
CRIT_GREEN  = "#059669"
CRIT_AMBER  = "#F59E0B"

# Criterio → color (índice: punct, contrib, commit, attitude)
CRITERION_COLORS = [CRIT_BLUE, CRIT_PURPLE, CRIT_GREEN, CRIT_AMBER]

# ── TK — Teacher Kit (modo oscuro) ────────────────────────────────────────────
TK_BACKGROUND  = "#0E1117"
TK_SURFACE     = "#161B25"
TK_SURFACE_ALT = "#1E2535"
TK_BORDER      = "#262E40"
TK_TEXT        = "#F0F2F8"
TK_TEXT_MID    = "#8892A4"
TK_TEXT_FAINT  = "#4A5568"
TK_GOLD        = "#C9A84C"
TK_GOLD_LIGHT  = "#18C9A84C"   # con alfa 0x18
TK_GOLD_BORDER = "#35C9A84C"   # con alfa 0x35
TK_SUCCESS     = "#34D399"
TK_WARNING     = "#FBBF24"
TK_DANGER      = "#F87171"
TK_BLUE        = "#60A5FA"
TK_PURPLE      = "#A78BFA"
TK_PINK        = "#F9A8D4"

# Criterio → color (modo oscuro)
CRITERION_COLORS_DARK = [TK_BLUE, TK_PURPLE, TK_SUCCESS, TK_PINK]
```

- [ ] **Step 2: Commit**

```bash
git add src/presentation/theme/
git commit -m "feat: SK/TK color palettes"
```

---

## Task 9: ViewModels

**Files:**
- Create: `src/presentation/viewmodels/login_viewmodel.py`
- Create: `src/presentation/viewmodels/student_viewmodel.py`
- Create: `src/presentation/viewmodels/teacher_viewmodel.py`
- Test: `tests/presentation/test_student_viewmodel.py`

- [ ] **Step 1: Escribir tests del StudentViewModel**

```python
# tests/presentation/test_student_viewmodel.py
import sqlite3
import pytest
from src.data.services.database_service import DatabaseService
from src.data.repositories.auth_repository_impl import AuthRepositoryImpl
from src.data.repositories.evaluation_repository_impl import EvaluationRepositoryImpl
from src.presentation.viewmodels.student_viewmodel import StudentViewModel, EvalStudentStatus


@pytest.fixture
def vm(tmp_path):
    db = DatabaseService(db_path=str(tmp_path / "test.db"))
    auth = AuthRepositoryImpl(db)
    eval_repo = EvaluationRepositoryImpl(db)
    notify_calls = []
    vm = StudentViewModel(auth_repo=auth, eval_repo=eval_repo, notify=lambda: notify_calls.append(1))
    vm._notify_calls = notify_calls
    return vm


def test_initial_state(vm):
    assert vm.student is None
    assert vm.is_logged_in is False
    assert vm.is_loading is False
    assert vm.evaluations == []


def test_check_session_no_session_leaves_student_none(vm):
    vm.check_session()
    assert vm.student is None


def test_register_sets_student(vm):
    vm.register("Ana López", "ana@uni.edu", "secret123")
    assert vm.student is not None
    assert vm.student.email == "ana@uni.edu"
    assert vm.is_logged_in is True


def test_logout_clears_student(vm):
    vm.register("Ana López", "ana@uni.edu", "secret123")
    vm.logout()
    assert vm.student is None
    assert vm.is_logged_in is False


def test_register_duplicate_email_sets_auth_error(vm):
    vm.register("Ana", "ana@uni.edu", "pass1")
    vm.register("Ana 2", "ana@uni.edu", "pass2")
    assert "registrado" in vm.auth_error.lower()


def test_performance_badge_thresholds():
    from src.domain.models.peer_evaluation import CriterionResult
    vm_bare = StudentViewModel.__new__(StudentViewModel)
    vm_bare.my_results = [CriterionResult(label="X", value=4.6)]
    assert "Excelente" in vm_bare.performance_badge
    vm_bare.my_results = [CriterionResult(label="X", value=3.6)]
    assert "Buen" in vm_bare.performance_badge
    vm_bare.my_results = [CriterionResult(label="X", value=2.6)]
    assert "adecuado" in vm_bare.performance_badge.lower()
    vm_bare.my_results = [CriterionResult(label="X", value=2.0)]
    assert "Necesita" in vm_bare.performance_badge
```

- [ ] **Step 2: Ejecutar tests**

```bash
pytest tests/presentation/test_student_viewmodel.py -v
```
Expected: `ImportError`

- [ ] **Step 3: Crear LoginViewModel**

```python
# src/presentation/viewmodels/login_viewmodel.py
from __future__ import annotations
from typing import Callable

from src.domain.models.auth_login_result import AuthLoginResult
from src.domain.repositories.i_unified_auth_repository import IUnifiedAuthRepository


class LoginViewModel:
    def __init__(
        self,
        unified_auth: IUnifiedAuthRepository,
        notify: Callable[[], None] | None = None,
    ) -> None:
        self._auth = unified_auth
        self._notify = notify or (lambda: None)

        self.is_loading: bool = False
        self.auth_error: str = ""

    def login(self, email: str, password: str) -> AuthLoginResult | None:
        if not email.strip() or not password:
            self.auth_error = "Completa todos los campos"
            self._notify()
            return None
        self.is_loading = True
        self.auth_error = ""
        self._notify()
        try:
            result = self._auth.login_and_resolve(email, password)
            if result is None:
                self.auth_error = "Correo o contraseña incorrectos"
                self._notify()
                return None
            return result
        except Exception:
            self.auth_error = "Error al conectar con la base de datos"
            self._notify()
            return None
        finally:
            self.is_loading = False
            self._notify()

    def clear_error(self) -> None:
        self.auth_error = ""
        self._notify()
```

- [ ] **Step 4: Crear StudentViewModel**

```python
# src/presentation/viewmodels/student_viewmodel.py
from __future__ import annotations
from enum import Enum
from typing import Callable

from src.domain.models.evaluation import Evaluation
from src.domain.models.peer_evaluation import Peer, CriterionResult, EvalCriterion
from src.domain.models.student import Student
from src.domain.repositories.i_auth_repository import IAuthRepository
from src.domain.repositories.i_evaluation_repository import IEvaluationRepository


class EvalStudentStatus(Enum):
    active_pending   = "active_pending"    # activa, no completada
    active_completed = "active_completed"  # activa, ya evaluó a todos
    closed_not_done  = "closed_not_done"   # cerrada, no la realizó
    closed_completed = "closed_completed"  # cerrada, la realizó


class StudentViewModel:
    def __init__(
        self,
        auth_repo: IAuthRepository,
        eval_repo: IEvaluationRepository,
        notify: Callable[[], None] | None = None,
    ) -> None:
        self._auth = auth_repo
        self._eval = eval_repo
        self._notify = notify or (lambda: None)

        # Auth state
        self.student: Student | None = None
        self.is_loading: bool = False
        self.auth_error: str = ""

        # Eval state
        self.evaluations: list[Evaluation] = []
        self.eval_statuses: dict[int, EvalStudentStatus] = {}
        self.active_eval: Evaluation | None = None
        self.current_group_name: str = ""
        self.has_active_eval: bool = False

        # Peers state
        self.peers: list[Peer] = []
        self.current_peer: Peer | None = None
        self.scores: dict[str, int] = {}

        # Results state
        self.my_results: list[CriterionResult] = []

    @property
    def is_logged_in(self) -> bool:
        return self.student is not None

    @property
    def done_count(self) -> int:
        return sum(1 for p in self.peers if p.evaluated)

    @property
    def total_peers(self) -> int:
        return len(self.peers)

    @property
    def eval_progress(self) -> float:
        return 0.0 if self.total_peers == 0 else self.done_count / self.total_peers

    @property
    def all_evaluated(self) -> bool:
        return self.total_peers > 0 and self.done_count == self.total_peers

    @property
    def all_criteria_scored(self) -> bool:
        return all(c.id in self.scores for c in EvalCriterion.DEFAULTS)

    @property
    def my_average(self) -> float:
        if not self.my_results:
            return 0.0
        return sum(r.value for r in self.my_results) / len(self.my_results)

    @property
    def performance_badge(self) -> str:
        avg = self.my_average
        if avg >= 4.5:
            return "Excelente desempeño"
        if avg >= 3.5:
            return "Buen desempeño"
        if avg >= 2.5:
            return "Desempeño adecuado"
        return "Necesita mejorar"

    # ── Auth ──────────────────────────────────────────────────────────────────

    def check_session(self) -> None:
        self.is_loading = True
        self._notify()
        try:
            self.student = self._auth.get_current_session()
            if self.student:
                self._load_eval_data()
        finally:
            self.is_loading = False
            self._notify()

    def register(self, name: str, email: str, password: str) -> bool:
        self.is_loading = True
        self.auth_error = ""
        self._notify()
        try:
            self.student = self._auth.register(name, email, password)
            self._load_eval_data()
            return True
        except Exception:
            self.auth_error = "El correo ya está registrado"
            return False
        finally:
            self.is_loading = False
            self._notify()

    def logout(self) -> None:
        self._auth.logout()
        self.student = None
        self._reset_eval_state()
        self._notify()

    # ── Eval data ─────────────────────────────────────────────────────────────

    def _load_eval_data(self) -> None:
        s = self.student
        if s is None:
            return
        student_id = int(s.id)
        try:
            eval_list = self._eval.get_evaluations_for_student(s.email)
            self.evaluations = eval_list
        except Exception:
            eval_list = []
            self.evaluations = []

        self._compute_statuses(eval_list, s.email, student_id)

        # Pick best eval: first active+pending, then any active, then first
        eval_ctx = (
            next(
                (e for e in eval_list if self.eval_statuses.get(e.id) == EvalStudentStatus.active_pending),
                None,
            )
            or next((e for e in eval_list if e.is_active), None)
            or (eval_list[0] if eval_list else None)
        )
        self.active_eval = eval_ctx
        if eval_ctx is None:
            self.has_active_eval = False
            self.peers = []
            self.my_results = []
            self.current_group_name = ""
            return
        self.has_active_eval = eval_ctx.is_active
        self._load_group_and_peers(eval_ctx, s)
        self._load_my_results(eval_ctx.id, s.email)

    def _compute_statuses(
        self, eval_list: list[Evaluation], email: str, student_id: int
    ) -> None:
        statuses: dict[int, EvalStudentStatus] = {}
        for ev in eval_list:
            try:
                completed = self._eval.has_completed_all_peers(
                    eval_id=ev.id, email=email, student_id=student_id
                )
                if ev.is_active:
                    statuses[ev.id] = (
                        EvalStudentStatus.active_completed
                        if completed
                        else EvalStudentStatus.active_pending
                    )
                else:
                    statuses[ev.id] = (
                        EvalStudentStatus.closed_completed
                        if completed
                        else EvalStudentStatus.closed_not_done
                    )
            except Exception:
                statuses[ev.id] = (
                    EvalStudentStatus.active_pending
                    if ev.is_active
                    else EvalStudentStatus.closed_not_done
                )
        self.eval_statuses = statuses

    def _load_group_and_peers(self, ev: Evaluation, s: Student) -> None:
        try:
            gname = self._eval.get_group_name_for_student(ev.id, s.email)
            self.current_group_name = gname or ev.category_name
        except Exception:
            self.current_group_name = ev.category_name
        student_id = int(s.id)
        try:
            peer_list = self._eval.get_peers_for_student(ev.id, s.email)
            for p in peer_list:
                p.evaluated = self._eval.has_evaluated(
                    eval_id=ev.id,
                    evaluator_student_id=student_id,
                    evaluated_member_id=int(p.id),
                )
        except Exception:
            peer_list = []
        self.peers = peer_list

    def _load_my_results(self, eval_id: int, email: str) -> None:
        try:
            self.my_results = self._eval.get_my_results(eval_id, email)
        except Exception:
            self.my_results = []

    # ── Select eval for evaluation ─────────────────────────────────────────────

    def select_eval_for_evaluation(self, ev: Evaluation) -> None:
        s = self.student
        if s is None:
            return
        self.active_eval = ev
        self.has_active_eval = ev.is_active
        self.peers = []
        self.my_results = []
        self._load_group_and_peers(ev, s)
        self._notify()

    def select_eval_for_results(self, ev: Evaluation) -> None:
        s = self.student
        if s is None:
            return
        self.active_eval = ev
        try:
            gname = self._eval.get_group_name_for_student(ev.id, s.email)
            self.current_group_name = gname or ev.category_name
        except Exception:
            self.current_group_name = ev.category_name
        self._load_my_results(ev.id, s.email)
        self._notify()

    # ── Peer scoring ──────────────────────────────────────────────────────────

    def select_peer(self, peer: Peer) -> None:
        self.current_peer = peer
        self.scores = dict(peer.scores)
        self._notify()

    def set_score(self, criterion_id: str, score: int) -> None:
        self.scores[criterion_id] = score

    def save_peer_score(self) -> None:
        peer = self.current_peer
        if peer is None or not self.all_criteria_scored:
            return
        peer.scores = dict(self.scores)
        peer.evaluated = True
        self._notify()

    def submit_evaluation(self) -> None:
        s = self.student
        ev = self.active_eval
        if s is None or ev is None:
            return
        student_id = int(s.id)
        for peer in self.peers:
            if peer.evaluated and peer.scores:
                try:
                    self._eval.save_responses(
                        eval_id=ev.id,
                        evaluator_student_id=student_id,
                        evaluated_member_id=int(peer.id),
                        scores=peer.scores,
                    )
                except Exception:
                    pass
        self._load_my_results(ev.id, s.email)
        try:
            completed = self._eval.has_completed_all_peers(
                eval_id=ev.id, email=s.email, student_id=student_id
            )
            self.eval_statuses[ev.id] = (
                EvalStudentStatus.active_completed
                if (ev.is_active and completed)
                else EvalStudentStatus.closed_completed
                if completed
                else EvalStudentStatus.active_pending
                if ev.is_active
                else EvalStudentStatus.closed_not_done
            )
        except Exception:
            pass
        self._notify()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _reset_eval_state(self) -> None:
        self.active_eval = None
        self.has_active_eval = False
        self.current_group_name = ""
        self.evaluations = []
        self.eval_statuses = {}
        self.peers = []
        self.my_results = []
        self.current_peer = None
        self.scores = {}
```

- [ ] **Step 5: Crear TeacherViewModel**

```python
# src/presentation/viewmodels/teacher_viewmodel.py
from __future__ import annotations
from typing import Callable

from src.domain.models.course import CourseModel
from src.domain.models.evaluation import Evaluation
from src.domain.models.group_category import GroupCategory
from src.domain.models.teacher import Teacher
from src.domain.models.teacher_data import GroupResult
from src.domain.repositories.i_teacher_auth_repository import ITeacherAuthRepository
from src.domain.repositories.i_group_repository import IGroupRepository
from src.domain.repositories.i_evaluation_repository import IEvaluationRepository
from src.domain.repositories.i_course_repository import ICourseRepository


class TeacherViewModel:
    def __init__(
        self,
        auth_repo: ITeacherAuthRepository,
        group_repo: IGroupRepository,
        eval_repo: IEvaluationRepository,
        course_repo: ICourseRepository,
        notify: Callable[[], None] | None = None,
    ) -> None:
        self._auth = auth_repo
        self._group = group_repo
        self._eval = eval_repo
        self._course = course_repo
        self._notify = notify or (lambda: None)

        # Auth
        self.teacher: Teacher | None = None
        self.is_loading: bool = False
        self.auth_error: str = ""

        # Courses
        self.courses: list[CourseModel] = []
        self.selected_course_id: int | None = None
        self.selected_course_name: str = ""
        self.categories_for_course: list[GroupCategory] = []

        # Groups / categories
        self.categories: list[GroupCategory] = []
        self.import_loading: bool = False
        self.import_error: str = ""

        # Evaluations
        self.evaluations: list[Evaluation] = []
        self.active_eval: Evaluation | None = None

        # New evaluation form
        self.eval_name: str = "Sprint 2 Review"
        self.selected_hours: int = 48
        self.selected_visibility: str = "private"
        self.selected_category_id: int | None = None
        self.selected_category_name: str = ""
        self.eval_error: str = ""

        # Results drill-down
        self.group_results: list[GroupResult] = []
        self.results_loading: bool = False
        self.selected_eval_for_results: Evaluation | None = None
        self.drill_group_index: int | None = None

    @property
    def is_logged_in(self) -> bool:
        return self.teacher is not None

    @property
    def total_groups(self) -> int:
        return sum(c.group_count for c in self.categories)

    @property
    def overall_average(self) -> float:
        non_zero = [g.average for g in self.group_results if g.average > 0]
        return round(sum(non_zero) / len(non_zero), 1) if non_zero else 0.0

    # ── Auth ──────────────────────────────────────────────────────────────────

    def check_session(self) -> None:
        self.is_loading = True
        self._notify()
        try:
            self.teacher = self._auth.get_current_session()
            if self.teacher:
                self._on_login()
        finally:
            self.is_loading = False
            self._notify()

    def register(self, name: str, email: str, password: str) -> bool:
        self.is_loading = True
        self.auth_error = ""
        self._notify()
        try:
            self.teacher = self._auth.register(name, email, password)
            self._on_login()
            return True
        except Exception:
            self.auth_error = "El correo ya está registrado"
            return False
        finally:
            self.is_loading = False
            self._notify()

    def logout(self) -> None:
        self._auth.logout()
        self.teacher = None
        self._notify()

    def _on_login(self) -> None:
        self.load_courses()
        self.load_categories()
        self.load_evaluations()

    # ── Courses ───────────────────────────────────────────────────────────────

    def load_courses(self) -> None:
        tid = self._teacher_id()
        try:
            self.courses = self._course.get_all(tid)
        except Exception:
            self.courses = []
        self._notify()

    def create_course(self, name: str, code: str) -> None:
        tid = self._teacher_id()
        course = self._course.create(name=name, code=code, teacher_id=tid)
        self.courses.insert(0, course)
        self._notify()

    def delete_course(self, course_id: int) -> None:
        self._course.delete(course_id)
        self.courses = [c for c in self.courses if c.id != course_id]
        if self.selected_course_id == course_id:
            self.selected_course_id = None
            self.selected_course_name = ""
            self.categories_for_course = []
        self._notify()

    def load_categories_for_course(self, course_id: int) -> None:
        self.selected_course_id = course_id
        course = next((c for c in self.courses if c.id == course_id), None)
        self.selected_course_name = course.name if course else ""
        try:
            self.categories_for_course = self._course.get_categories_for_course(course_id)
        except Exception:
            self.categories_for_course = []
        self._notify()

    # ── Categories / CSV ──────────────────────────────────────────────────────

    def load_categories(self) -> None:
        tid = self._teacher_id()
        try:
            cats = self._group.get_all(tid)
            self.categories = cats
            if cats and self.selected_category_id is None:
                self.selected_category_id = cats[0].id
                self.selected_category_name = cats[0].name
        except Exception:
            self.categories = []
        self._notify()

    def import_csv(self, csv_content: str, category_name: str, course_id: int) -> None:
        self.import_loading = True
        self.import_error = ""
        tid = self._teacher_id()
        self._notify()
        try:
            cat = self._group.import_csv(csv_content, category_name, tid, course_id)
            self.categories.insert(0, cat)
            if self.selected_category_id is None:
                self.selected_category_id = cat.id
                self.selected_category_name = cat.name
        except Exception as e:
            self.import_error = f"Error al importar: {e}"
        finally:
            self.import_loading = False
            self._notify()

    def delete_category(self, category_id: int) -> None:
        self._group.delete(category_id)
        self.categories = [c for c in self.categories if c.id != category_id]
        if self.selected_category_id == category_id:
            self.selected_category_id = (
                self.categories[0].id if self.categories else None
            )
            self.selected_category_name = (
                self.categories[0].name if self.categories else ""
            )
        self._notify()

    # ── Evaluations ───────────────────────────────────────────────────────────

    def load_evaluations(self) -> None:
        tid = self._teacher_id()
        try:
            all_evals = self._eval.get_all(tid)
            self.evaluations = all_evals
            self.active_eval = next((e for e in all_evals if e.is_active), None)
        except Exception:
            self.evaluations = []
            self.active_eval = None
        self._notify()

    def create_evaluation(self) -> str | None:
        """Crea evaluación. Devuelve None en éxito, mensaje de error si falla."""
        if self.selected_course_id is None:
            return "Selecciona un curso"
        if self.selected_category_id is None:
            return "Selecciona una categoría de grupos"
        tid = self._teacher_id()
        self.is_loading = True
        self.eval_error = ""
        self._notify()
        try:
            ev = self._eval.create(
                name=self.eval_name,
                category_id=self.selected_category_id,
                hours=self.selected_hours,
                visibility=self.selected_visibility,
                teacher_id=tid,
            )
            self.evaluations.insert(0, ev)
            if ev.is_active:
                self.active_eval = ev
            return None
        except Exception as e:
            self.eval_error = str(e)
            return str(e)
        finally:
            self.is_loading = False
            self._notify()

    def rename_evaluation(self, eval_id: int, new_name: str) -> None:
        tid = self._teacher_id()
        self._eval.rename(eval_id, new_name, tid)
        self.evaluations = [
            Evaluation(
                id=e.id,
                name=new_name if e.id == eval_id else e.name,
                category_id=e.category_id,
                category_name=e.category_name,
                course_name=e.course_name,
                hours=e.hours,
                visibility=e.visibility,
                created_at=e.created_at,
                closes_at=e.closes_at,
            )
            for e in self.evaluations
        ]
        if self.active_eval and self.active_eval.id == eval_id:
            self.active_eval = next(
                (e for e in self.evaluations if e.id == eval_id), None
            )
        self._notify()

    def delete_evaluation(self, eval_id: int) -> None:
        self._eval.delete(eval_id)
        self.evaluations = [e for e in self.evaluations if e.id != eval_id]
        if self.active_eval and self.active_eval.id == eval_id:
            self.active_eval = next((e for e in self.evaluations if e.is_active), None)
        self._notify()

    # ── Results ───────────────────────────────────────────────────────────────

    def load_group_results(self, ev: Evaluation) -> None:
        self.selected_eval_for_results = ev
        self.drill_group_index = None
        self.results_loading = True
        self._notify()
        try:
            self.group_results = self._eval.get_group_results(ev.id)
        except Exception:
            self.group_results = []
        finally:
            self.results_loading = False
            self._notify()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _teacher_id(self) -> int:
        return int(self.teacher.id) if self.teacher else 0
```

- [ ] **Step 6: Ejecutar tests**

```bash
pytest tests/presentation/test_student_viewmodel.py -v
```
Expected: todos PASS

- [ ] **Step 7: Commit**

```bash
git add src/presentation/viewmodels/ tests/presentation/test_student_viewmodel.py
git commit -m "feat: login/student/teacher viewmodels"
```

---

## Task 10: Componentes compartidos

**Files:**
- Create: `src/presentation/components/avatar_circle.py`

- [ ] **Step 1: Crear componente AvatarCircle reutilizable**

```python
# src/presentation/components/avatar_circle.py
"""Componente de avatar circular con iniciales, reutilizado en toda la app."""
from __future__ import annotations
import flet as ft


def avatar_circle(
    initials: str,
    size: int = 40,
    bg_color: str = "#7C83D6",
    text_color: str = "#FFFFFF",
    font_size: int = 14,
) -> ft.Container:
    return ft.Container(
        width=size,
        height=size,
        bgcolor=bg_color,
        border_radius=size // 2,
        alignment=ft.alignment.center,
        content=ft.Text(
            initials[:2].upper(),
            size=font_size,
            weight=ft.FontWeight.BOLD,
            color=text_color,
        ),
    )
```

- [ ] **Step 2: Commit**

```bash
git add src/presentation/components/avatar_circle.py
git commit -m "feat: reusable avatar_circle component"
```

---

## Task 11: Main.py — DI, Router, Splash

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Reescribir main.py completo**

```python
# main.py
"""EvalUn — entrada de la aplicación.

Wiring de dependencias (manual DI) y router Flet.

Ejecución local:
    python main.py

Empaquetado móvil:
    flet build apk
    flet build ipa
"""
from __future__ import annotations

import flet as ft

from src.data.services.database_service import DatabaseService
from src.data.repositories.auth_repository_impl import AuthRepositoryImpl
from src.data.repositories.teacher_auth_repository_impl import TeacherAuthRepositoryImpl
from src.data.repositories.unified_auth_repository_impl import UnifiedAuthRepositoryImpl
from src.data.repositories.group_repository_impl import GroupRepositoryImpl
from src.data.repositories.course_repository_impl import CourseRepositoryImpl
from src.data.repositories.evaluation_repository_impl import EvaluationRepositoryImpl

from src.presentation.theme.app_colors import SK_BACKGROUND, SK_PRIMARY, TK_BACKGROUND, TK_GOLD
from src.presentation.viewmodels.login_viewmodel import LoginViewModel
from src.presentation.viewmodels.student_viewmodel import StudentViewModel
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel

from src.presentation.pages.auth.login_page import login_page
from src.presentation.pages.auth.register_page import register_page
from src.presentation.pages.student.s_courses_page import s_courses_page
from src.presentation.pages.student.s_eval_list_page import s_eval_list_page
from src.presentation.pages.student.s_peers_page import s_peers_page
from src.presentation.pages.student.s_peer_score_page import s_peer_score_page
from src.presentation.pages.student.s_my_results_page import s_my_results_page
from src.presentation.pages.teacher.t_dash_page import t_dash_page
from src.presentation.pages.teacher.t_import_page import t_import_page
from src.presentation.pages.teacher.t_new_eval_page import t_new_eval_page
from src.presentation.pages.teacher.t_results_page import t_results_page
from src.presentation.pages.teacher.t_profile_page import t_profile_page
from src.presentation.pages.teacher.t_course_manage_page import t_course_manage_page


def main(page: ft.Page) -> None:
    # ── App settings ──────────────────────────────────────────────────────────
    page.title = "EvalUn"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0
    page.fonts = {}  # custom fonts can be added here

    # ── DI ────────────────────────────────────────────────────────────────────
    db = DatabaseService()
    student_auth = AuthRepositoryImpl(db)
    teacher_auth = TeacherAuthRepositoryImpl(db)
    unified_auth = UnifiedAuthRepositoryImpl(student_auth, teacher_auth)
    group_repo   = GroupRepositoryImpl(db)
    course_repo  = CourseRepositoryImpl(db)
    eval_repo    = EvaluationRepositoryImpl(db)

    login_vm   = LoginViewModel(unified_auth)
    student_vm = StudentViewModel(student_auth, eval_repo)
    teacher_vm = TeacherViewModel(teacher_auth, group_repo, eval_repo, course_repo)

    # ── Router ────────────────────────────────────────────────────────────────
    def route_change(e: ft.RouteChangeEvent) -> None:
        page.views.clear()
        r = page.route

        # Auth
        if r == "/login":
            page.views.append(login_page(page, login_vm, student_vm, teacher_vm))
        elif r == "/register":
            page.views.append(register_page(page, student_vm, teacher_vm))

        # Student
        elif r == "/student/courses":
            page.views.append(s_courses_page(page, student_vm))
        elif r == "/student/eval-list":
            page.views.append(s_eval_list_page(page, student_vm))
        elif r == "/student/peers":
            page.views.append(s_peers_page(page, student_vm))
        elif r == "/student/peer-score":
            page.views.append(s_peer_score_page(page, student_vm))
        elif r == "/student/results":
            page.views.append(s_my_results_page(page, student_vm))

        # Teacher
        elif r == "/teacher/dash":
            page.views.append(t_dash_page(page, teacher_vm))
        elif r == "/teacher/import":
            page.views.append(t_import_page(page, teacher_vm))
        elif r == "/teacher/new-eval":
            page.views.append(t_new_eval_page(page, teacher_vm))
        elif r == "/teacher/results":
            page.views.append(t_results_page(page, teacher_vm))
        elif r == "/teacher/profile":
            page.views.append(t_profile_page(page, teacher_vm))
        elif r == "/teacher/courses":
            page.views.append(t_course_manage_page(page, teacher_vm))

        # Splash / default
        else:
            page.views.append(_splash_view(page, student_vm, teacher_vm))

        page.update()

    def view_pop(e: ft.ViewPopEvent) -> None:
        page.views.pop()
        if page.views:
            page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")  # inicia en splash


def _splash_view(
    page: ft.Page,
    student_vm: StudentViewModel,
    teacher_vm: TeacherViewModel,
) -> ft.View:
    """Splash: restaura sesión y redirige."""

    def _resolve() -> None:
        try:
            student_vm.check_session()
            teacher_vm.check_session()
        except Exception:
            pass

        if teacher_vm.is_logged_in:
            page.go("/teacher/dash")
        elif student_vm.is_logged_in:
            page.go("/student/courses")
        else:
            page.go("/login")

    page.run_thread(_resolve)

    return ft.View(
        route="/",
        bgcolor=SK_BACKGROUND,
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.ProgressRing(color=SK_PRIMARY, stroke_width=2),
            )
        ],
    )


if __name__ == "__main__":
    ft.app(target=main)
```

- [ ] **Step 2: Verificar que la app arranca (aún sin páginas)**

```bash
python main.py
```
Expected: ventana con spinner (redirige a /login, que aún no existe → error manejado)

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: rewrite main.py with peerUn DI + router + splash"
```

---

## Task 12: Login Page

**Files:**
- Create: `src/presentation/pages/auth/__init__.py`
- Create: `src/presentation/pages/auth/login_page.py`

- [ ] **Step 1: Crear página de login**

```python
# src/presentation/pages/auth/__init__.py
```

```python
# src/presentation/pages/auth/login_page.py
"""Página de login unificado (estudiante o docente)."""
from __future__ import annotations

import flet as ft

from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_SURFACE_ALT, SK_BORDER, SK_TEXT,
    SK_TEXT_MID, SK_TEXT_FAINT, SK_PRIMARY, SK_PRIMARY_LIGHT,
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER, TK_TEXT,
    TK_TEXT_FAINT, TK_GOLD, TK_GOLD_LIGHT, TK_DANGER,
)
from src.presentation.viewmodels.login_viewmodel import LoginViewModel
from src.presentation.viewmodels.student_viewmodel import StudentViewModel
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def login_page(
    page: ft.Page,
    login_vm: LoginViewModel,
    student_vm: StudentViewModel,
    teacher_vm: TeacherViewModel,
) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK

    def _colors():
        nonlocal is_dark
        return {
            "bg":      TK_BACKGROUND  if is_dark else SK_BACKGROUND,
            "card":    TK_SURFACE     if is_dark else SK_SURFACE,
            "field":   TK_SURFACE_ALT if is_dark else SK_SURFACE_ALT,
            "border":  TK_BORDER      if is_dark else SK_BORDER,
            "text":    TK_TEXT        if is_dark else SK_TEXT,
            "muted":   TK_TEXT_FAINT  if is_dark else SK_TEXT_FAINT,
            "accent":  TK_GOLD        if is_dark else SK_PRIMARY,
            "error":   TK_DANGER      if is_dark else "#EF4444",
            "icon_bg": TK_GOLD_LIGHT  if is_dark else SK_PRIMARY_LIGHT,
        }

    email_field    = ft.TextField(hint_text="Correo institucional", password=False,
                                  prefix_icon=ft.Icons.MAIL_OUTLINE_ROUNDED,
                                  expand=True)
    password_field = ft.TextField(hint_text="Contraseña", password=True,
                                  can_reveal_password=True,
                                  prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED,
                                  expand=True)
    error_text     = ft.Text("", color=_colors()["error"], size=12, visible=False)
    login_btn      = ft.ElevatedButton(
        "Iniciar sesión",
        expand=True,
        style=ft.ButtonStyle(bgcolor=SK_PRIMARY, color="#FFFFFF"),
    )
    register_btn   = ft.OutlinedButton("Crear cuenta", expand=True)
    theme_icon     = ft.IconButton(
        icon=ft.Icons.DARK_MODE_ROUNDED if not is_dark else ft.Icons.LIGHT_MODE_ROUNDED
    )

    def _apply_colors() -> None:
        c = _colors()
        email_field.focused_border_color    = c["accent"]
        password_field.focused_border_color = c["accent"]
        error_text.color                    = c["error"]
        login_btn.style                     = ft.ButtonStyle(bgcolor=c["accent"], color="#FFFFFF")
        view.bgcolor                        = c["bg"]

    def _notify() -> None:
        error_text.value   = login_vm.auth_error
        error_text.visible = bool(login_vm.auth_error)
        login_btn.disabled = login_vm.is_loading
        login_btn.text     = "Iniciando..." if login_vm.is_loading else "Iniciar sesión"
        page.update()

    login_vm._notify = _notify

    def _on_login(_) -> None:
        def _do() -> None:
            result = login_vm.login(email_field.value or "", password_field.value or "")
            if result is None:
                return
            if result.role.value == "teacher":
                teacher_vm.check_session()
                student_vm.student = None
            else:
                student_vm.check_session()
                teacher_vm.teacher = None
            page.go(result.home_route)

        page.run_thread(_do)

    def _on_register(_) -> None:
        login_vm.clear_error()
        page.go("/register")

    def _toggle_theme(_) -> None:
        nonlocal is_dark
        is_dark = not is_dark
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        theme_icon.icon = (
            ft.Icons.LIGHT_MODE_ROUNDED if is_dark else ft.Icons.DARK_MODE_ROUNDED
        )
        _apply_colors()
        page.update()

    login_btn.on_click    = _on_login
    register_btn.on_click = _on_register
    theme_icon.on_click   = _toggle_theme

    view = ft.View(
        route="/login",
        bgcolor=SK_BACKGROUND,
        padding=24,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Container(
                    expand=True,
                    bgcolor=SK_SURFACE,
                    border_radius=18,
                    border=ft.border.all(1, SK_BORDER),
                    padding=20,
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        expand=True,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        width=44, height=44,
                                        bgcolor=SK_PRIMARY_LIGHT,
                                        border_radius=12,
                                        alignment=ft.alignment.center,
                                        content=ft.Icon(ft.Icons.SCHOOL_ROUNDED, color=SK_PRIMARY, size=24),
                                    ),
                                    ft.Container(expand=True),
                                    theme_icon,
                                ]
                            ),
                            ft.Text(
                                "Bienvenido a EvalUn",
                                size=24, weight=ft.FontWeight.W_800,
                                color=SK_TEXT,
                            ),
                            ft.Container(height=8),
                            email_field,
                            ft.Container(height=4),
                            password_field,
                            ft.Container(height=4),
                            error_text,
                            ft.Container(height=4),
                            login_btn,
                            ft.Container(height=8),
                            ft.Text(
                                "¿No tienes cuenta?",
                                size=12, color=SK_TEXT_FAINT,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            register_btn,
                            ft.Container(height=8),
                            ft.Text(
                                "Autenticado por Roble SSO",
                                size=11, color=SK_TEXT_FAINT,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),
                ),
            )
        ],
    )
    _apply_colors()
    return view
```

- [ ] **Step 2: Ejecutar app y verificar login page renderiza**

```bash
python main.py
```
Expected: pantalla de login visible con campos email/password y botones

- [ ] **Step 3: Commit**

```bash
git add src/presentation/pages/auth/
git commit -m "feat: login page"
```

---

## Task 13: Register Page

**Files:**
- Create: `src/presentation/pages/auth/register_page.py`

- [ ] **Step 1: Crear página de registro**

```python
# src/presentation/pages/auth/register_page.py
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_BORDER, SK_TEXT, SK_TEXT_FAINT,
    SK_PRIMARY, SK_PRIMARY_LIGHT,
)
from src.presentation.viewmodels.student_viewmodel import StudentViewModel
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def register_page(
    page: ft.Page,
    student_vm: StudentViewModel,
    teacher_vm: TeacherViewModel,
) -> ft.View:
    name_field     = ft.TextField(hint_text="Nombre completo", prefix_icon=ft.Icons.PERSON_OUTLINE_ROUNDED, expand=True)
    email_field    = ft.TextField(hint_text="Correo institucional", prefix_icon=ft.Icons.MAIL_OUTLINE_ROUNDED, expand=True)
    password_field = ft.TextField(hint_text="Contraseña", password=True, can_reveal_password=True,
                                  prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED, expand=True)
    confirm_field  = ft.TextField(hint_text="Confirmar contraseña", password=True, can_reveal_password=True,
                                  prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED, expand=True)
    error_text     = ft.Text("", color="#EF4444", size=12, visible=False)
    role_tabs      = ft.Tabs(
        tabs=[ft.Tab(text="Estudiante"), ft.Tab(text="Docente")],
        selected_index=0, expand=1,
    )
    register_btn = ft.ElevatedButton(
        "Crear cuenta", expand=True,
        style=ft.ButtonStyle(bgcolor=SK_PRIMARY, color="#FFFFFF"),
    )

    def _notify() -> None:
        vm = student_vm if role_tabs.selected_index == 0 else teacher_vm
        error_text.value   = vm.auth_error
        error_text.visible = bool(vm.auth_error)
        register_btn.disabled = vm.is_loading
        register_btn.text  = "Creando..." if vm.is_loading else "Crear cuenta"
        page.update()

    student_vm._notify = _notify
    teacher_vm._notify = _notify

    def _on_register(_) -> None:
        name     = name_field.value or ""
        email    = email_field.value or ""
        password = password_field.value or ""
        confirm  = confirm_field.value or ""

        if not name.strip() or not email.strip() or not password:
            error_text.value   = "Completa todos los campos"
            error_text.visible = True
            page.update()
            return
        if password != confirm:
            error_text.value   = "Las contraseñas no coinciden"
            error_text.visible = True
            page.update()
            return

        is_teacher = role_tabs.selected_index == 1

        def _do() -> None:
            if is_teacher:
                ok = teacher_vm.register(name, email, password)
                if ok:
                    page.go("/teacher/dash")
            else:
                ok = student_vm.register(name, email, password)
                if ok:
                    page.go("/student/courses")

        page.run_thread(_do)

    register_btn.on_click = _on_register

    return ft.View(
        route="/register",
        bgcolor=SK_BACKGROUND,
        padding=24,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/login")),
            title=ft.Text("Crear cuenta", color=SK_TEXT),
            bgcolor=SK_BACKGROUND,
            elevation=0,
        ),
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Container(
                    expand=True,
                    bgcolor=SK_SURFACE,
                    border_radius=18,
                    border=ft.border.all(1, SK_BORDER),
                    padding=20,
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        spacing=10,
                        controls=[
                            ft.Container(
                                width=44, height=44,
                                bgcolor=SK_PRIMARY_LIGHT,
                                border_radius=12,
                                alignment=ft.alignment.center,
                                content=ft.Icon(ft.Icons.SCHOOL_ROUNDED, color=SK_PRIMARY, size=24),
                            ),
                            ft.Text("Registro", size=22, weight=ft.FontWeight.W_700, color=SK_TEXT),
                            role_tabs,
                            name_field,
                            email_field,
                            password_field,
                            confirm_field,
                            error_text,
                            register_btn,
                        ],
                    ),
                ),
            )
        ],
    )
```

- [ ] **Step 2: Commit**

```bash
git add src/presentation/pages/auth/register_page.py
git commit -m "feat: register page (student/teacher via tabs)"
```

---

## Task 14: Student — Courses Page

**Files:**
- Create: `src/presentation/pages/student/__init__.py`
- Create: `src/presentation/pages/student/s_courses_page.py`

- [ ] **Step 1: Crear página principal del estudiante**

```python
# src/presentation/pages/student/__init__.py
```

```python
# src/presentation/pages/student/s_courses_page.py
"""SCoursesPage — pantalla principal del estudiante ('Mis evaluaciones')."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_SURFACE_ALT, SK_BORDER, SK_BORDER_MID,
    SK_TEXT, SK_TEXT_MID, SK_TEXT_FAINT, SK_PRIMARY, SK_PRIMARY_LIGHT,
)
from src.presentation.components.avatar_circle import avatar_circle
from src.presentation.viewmodels.student_viewmodel import StudentViewModel, EvalStudentStatus


def s_courses_page(page: ft.Page, vm: StudentViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _status_badge(status: EvalStudentStatus) -> ft.Container:
        label_map = {
            EvalStudentStatus.active_pending:   ("Pendiente",  "#7C83D6", "#EEEFFE"),
            EvalStudentStatus.active_completed: ("Completada", "#059669", "#ECFDF5"),
            EvalStudentStatus.closed_completed: ("Cerrada ✓",  "#6B7280", "#F3F4F6"),
            EvalStudentStatus.closed_not_done:  ("Cerrada",    "#EF4444", "#FEF2F2"),
        }
        text, color, bg = label_map.get(status, ("—", SK_TEXT_FAINT, SK_SURFACE_ALT))
        return ft.Container(
            bgcolor=bg,
            border_radius=6,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            content=ft.Text(text, size=10, color=color, weight=ft.FontWeight.W_600),
        )

    def _eval_card(ev) -> ft.Container:
        status = vm.eval_statuses.get(ev.id, EvalStudentStatus.active_pending)
        is_active = ev.is_active

        def _on_evaluate(_) -> None:
            vm.select_eval_for_evaluation(ev)
            page.go("/student/peers")

        def _on_results(_) -> None:
            vm.select_eval_for_results(ev)
            page.go("/student/results")

        actions = []
        if is_active and status == EvalStudentStatus.active_pending:
            actions.append(
                ft.ElevatedButton(
                    "Evaluar", on_click=_on_evaluate,
                    style=ft.ButtonStyle(bgcolor=SK_PRIMARY, color="#FFFFFF"),
                )
            )
        actions.append(
            ft.OutlinedButton("Ver resultados", on_click=_on_results)
        )

        return ft.Container(
            bgcolor=SK_SURFACE,
            border_radius=14,
            border=ft.border.all(1, SK_BORDER),
            padding=16,
            margin=ft.margin.only(bottom=10),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                expand=True,
                                spacing=2,
                                controls=[
                                    ft.Text(ev.name, size=14, weight=ft.FontWeight.W_600, color=SK_TEXT),
                                    ft.Text(ev.course_name or ev.category_name, size=12, color=SK_TEXT_FAINT),
                                ],
                            ),
                            _status_badge(status),
                        ]
                    ),
                    ft.Row(spacing=8, controls=actions),
                ],
            ),
        )

    def _hero_card() -> ft.Control:
        ev = vm.active_eval
        if ev is None or not ev.is_active:
            return ft.Container(height=0)
        status = vm.eval_statuses.get(ev.id, EvalStudentStatus.active_pending)
        done  = vm.done_count
        total = vm.total_peers
        prog  = vm.eval_progress

        def _on_evaluate(_) -> None:
            vm.select_eval_for_evaluation(ev)
            page.go("/student/peers")

        return ft.Container(
            bgcolor=SK_PRIMARY,
            border_radius=18,
            padding=20,
            margin=ft.margin.only(bottom=16),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text("Evaluación activa", size=11, color="#EEEFFE", weight=ft.FontWeight.W_600),
                    ft.Text(ev.name, size=18, weight=ft.FontWeight.W_800, color="#FFFFFF"),
                    ft.Text(ev.category_name, size=12, color="#EEEFFE"),
                    ft.Container(height=4),
                    ft.ProgressBar(value=prog, bgcolor="#EEEFFE", color="#FFFFFF"),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"{done}/{total} evaluados", size=11, color="#EEEFFE"),
                            ft.ElevatedButton(
                                "Evaluar ahora" if status == EvalStudentStatus.active_pending else "Completada",
                                disabled=status != EvalStudentStatus.active_pending,
                                on_click=_on_evaluate,
                                style=ft.ButtonStyle(bgcolor="#FFFFFF", color=SK_PRIMARY),
                            ),
                        ],
                    ),
                ],
            ),
        )

    def _profile_sheet() -> ft.BottomSheet:
        s = vm.student
        initials = s.initials if s else "?"
        name     = s.name    if s else ""
        email    = s.email   if s else ""

        def _logout(_) -> None:
            page.close(bs)
            def _do():
                vm.logout()
                page.go("/login")
            page.run_thread(_do)

        bs = ft.BottomSheet(
            open=True,
            content=ft.Container(
                padding=24,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.Row(
                            spacing=12,
                            controls=[
                                avatar_circle(initials, size=48, bg_color=SK_PRIMARY),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(name, size=16, weight=ft.FontWeight.W_600, color=SK_TEXT),
                                        ft.Text(email, size=12, color=SK_TEXT_FAINT),
                                    ],
                                ),
                            ],
                        ),
                        ft.Divider(),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.LOGOUT, color="#EF4444"),
                            title=ft.Text("Cerrar sesión", color="#EF4444"),
                            on_click=_logout,
                        ),
                    ],
                ),
            ),
        )
        return bs

    def _build_body() -> ft.Control:
        if vm.is_loading:
            return ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.ProgressRing(color=SK_PRIMARY),
            )
        evals = vm.evaluations
        if not evals:
            return ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.INBOX_OUTLINED, size=56, color=SK_TEXT_FAINT),
                        ft.Text("No tienes evaluaciones activas", color=SK_TEXT_FAINT, size=14),
                    ],
                ),
            )
        active  = [e for e in evals if e.is_active]
        closed  = [e for e in evals if not e.is_active]
        cards   = [_hero_card()]
        if active:
            cards.append(ft.Text("ACTIVAS", size=10, weight=ft.FontWeight.W_600,
                                 color=SK_TEXT_FAINT, letter_spacing=1.2))
            cards.extend(_eval_card(e) for e in active)
        if closed:
            cards.append(ft.Text("CERRADAS", size=10, weight=ft.FontWeight.W_600,
                                 color=SK_TEXT_FAINT, letter_spacing=1.2))
            cards.extend(_eval_card(e) for e in closed)
        return ft.ListView(controls=cards, expand=True, padding=ft.padding.symmetric(horizontal=16, vertical=8))

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify

    def _on_profile(_) -> None:
        page.open(_profile_sheet())

    def _on_history(_) -> None:
        page.go("/student/eval-list")

    page.run_thread(lambda: (vm.check_session() if not vm.is_logged_in else _notify()))

    content.content = _build_body()

    return ft.View(
        route="/student/courses",
        bgcolor=SK_BACKGROUND,
        appbar=ft.AppBar(
            title=ft.Text("Mis evaluaciones", color=SK_TEXT),
            bgcolor=SK_BACKGROUND,
            elevation=0,
            actions=[
                ft.IconButton(ft.Icons.HISTORY, tooltip="Historial", on_click=_on_history),
                ft.IconButton(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, tooltip="Perfil", on_click=_on_profile),
            ],
        ),
        controls=[content],
    )
```

- [ ] **Step 2: Commit**

```bash
git add src/presentation/pages/student/
git commit -m "feat: student courses page (main screen)"
```

---

## Task 15: Student — Eval List Page

**Files:**
- Create: `src/presentation/pages/student/s_eval_list_page.py`

- [ ] **Step 1: Crear historial de evaluaciones**

```python
# src/presentation/pages/student/s_eval_list_page.py
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_BORDER, SK_TEXT, SK_TEXT_FAINT, SK_PRIMARY,
)
from src.presentation.viewmodels.student_viewmodel import StudentViewModel, EvalStudentStatus


def s_eval_list_page(page: ft.Page, vm: StudentViewModel) -> ft.View:
    content = ft.Container(expand=True)

    STATUS_LABEL = {
        EvalStudentStatus.active_pending:   ("Pendiente",   "#7C83D6"),
        EvalStudentStatus.active_completed: ("Completada",  "#059669"),
        EvalStudentStatus.closed_completed: ("Cerrada ✓",   "#6B7280"),
        EvalStudentStatus.closed_not_done:  ("Cerrada",     "#EF4444"),
    }

    def _eval_row(ev) -> ft.Container:
        status = vm.eval_statuses.get(ev.id, EvalStudentStatus.active_pending)
        label, color = STATUS_LABEL.get(status, ("—", SK_TEXT_FAINT))

        def _evaluate(_) -> None:
            vm.select_eval_for_evaluation(ev)
            page.go("/student/peers")

        def _results(_) -> None:
            vm.select_eval_for_results(ev)
            page.go("/student/results")

        actions = []
        if ev.is_active and status == EvalStudentStatus.active_pending:
            actions.append(ft.TextButton("Evaluar", on_click=_evaluate))
        actions.append(ft.TextButton("Resultados", on_click=_results))

        return ft.Container(
            bgcolor=SK_SURFACE,
            border_radius=12,
            border=ft.border.all(1, SK_BORDER),
            padding=14,
            margin=ft.margin.only(bottom=8),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(ev.name, size=14, weight=ft.FontWeight.W_600, color=SK_TEXT),
                            ft.Container(
                                bgcolor=f"{color}22",
                                border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                content=ft.Text(label, size=10, color=color, weight=ft.FontWeight.W_600),
                            ),
                        ],
                    ),
                    ft.Text(
                        ev.course_name or ev.category_name,
                        size=11, color=SK_TEXT_FAINT,
                    ),
                    ft.Row(spacing=6, controls=actions),
                ],
            ),
        )

    def _build_body() -> ft.Control:
        evals = vm.evaluations
        if not evals:
            return ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Text("Sin evaluaciones", color=SK_TEXT_FAINT),
            )
        # Group by course_name
        groups: dict[str, list] = {}
        for ev in evals:
            key = ev.course_name or "Sin curso"
            groups.setdefault(key, []).append(ev)
        items: list[ft.Control] = []
        for course, evs in groups.items():
            items.append(
                ft.Container(
                    padding=ft.padding.only(top=12, bottom=4),
                    content=ft.Text(course.upper(), size=10, color=SK_TEXT_FAINT,
                                   weight=ft.FontWeight.W_600, letter_spacing=1.2),
                )
            )
            items.extend(_eval_row(ev) for ev in evs)
        return ft.ListView(
            controls=items, expand=True,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
        )

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify
    content.content = _build_body()

    return ft.View(
        route="/student/eval-list",
        bgcolor=SK_BACKGROUND,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/student/courses")),
            title=ft.Text("Historial", color=SK_TEXT),
            bgcolor=SK_BACKGROUND,
            elevation=0,
        ),
        controls=[content],
    )
```

- [ ] **Step 2: Commit**

```bash
git add src/presentation/pages/student/s_eval_list_page.py
git commit -m "feat: student eval-list page"
```

---

## Task 16: Student — Peers Page

**Files:**
- Create: `src/presentation/pages/student/s_peers_page.py`

- [ ] **Step 1: Crear página de compañeros**

```python
# src/presentation/pages/student/s_peers_page.py
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_BORDER, SK_TEXT, SK_TEXT_FAINT,
    SK_PRIMARY, SK_PRIMARY_LIGHT,
)
from src.presentation.components.avatar_circle import avatar_circle
from src.presentation.viewmodels.student_viewmodel import StudentViewModel


def s_peers_page(page: ft.Page, vm: StudentViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _peer_tile(peer) -> ft.Container:
        status_icon = ft.Icons.CHECK_CIRCLE if peer.evaluated else ft.Icons.RADIO_BUTTON_UNCHECKED
        status_color = "#059669" if peer.evaluated else SK_TEXT_FAINT

        def _on_tap(_) -> None:
            vm.select_peer(peer)
            page.go("/student/peer-score")

        return ft.Container(
            bgcolor=SK_SURFACE,
            border_radius=14,
            border=ft.border.all(1, SK_BORDER),
            padding=14,
            margin=ft.margin.only(bottom=8),
            on_click=_on_tap if not peer.evaluated else None,
            content=ft.Row(
                spacing=12,
                controls=[
                    avatar_circle(peer.initials, bg_color=SK_PRIMARY),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(peer.name, size=14, weight=ft.FontWeight.W_500, color=SK_TEXT),
                            ft.Text(
                                "Evaluación completada" if peer.evaluated else "Pendiente de evaluar",
                                size=11, color=status_color,
                            ),
                        ],
                    ),
                    ft.Icon(status_icon, color=status_color, size=20),
                ],
            ),
        )

    def _build_body() -> ft.Control:
        ev = vm.active_eval
        peers = vm.peers
        if not peers:
            return ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.GROUP_OUTLINED, size=56, color=SK_TEXT_FAINT),
                        ft.Text("No hay compañeros en esta evaluación", color=SK_TEXT_FAINT),
                    ],
                ),
            )

        done  = vm.done_count
        total = vm.total_peers

        submit_btn = ft.ElevatedButton(
            f"Enviar evaluación ({done}/{total})",
            disabled=not vm.all_evaluated,
            style=ft.ButtonStyle(bgcolor=SK_PRIMARY, color="#FFFFFF"),
            on_click=_on_submit,
            expand=True,
        )

        return ft.Column(
            expand=True,
            controls=[
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(ev.name if ev else "", size=16, weight=ft.FontWeight.W_700, color=SK_TEXT),
                            ft.Text(vm.current_group_name, size=12, color=SK_TEXT_FAINT),
                            ft.ProgressBar(value=vm.eval_progress, bgcolor=SK_PRIMARY_LIGHT, color=SK_PRIMARY),
                        ],
                    ),
                ),
                ft.ListView(
                    controls=[_peer_tile(p) for p in peers],
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=16),
                ),
                ft.Container(
                    padding=16,
                    content=submit_btn,
                ),
            ],
        )

    def _on_submit(_) -> None:
        def _do() -> None:
            vm.submit_evaluation()
            page.go("/student/courses")
        page.run_thread(_do)

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify
    content.content = _build_body()

    return ft.View(
        route="/student/peers",
        bgcolor=SK_BACKGROUND,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/student/courses")),
            title=ft.Text("Compañeros", color=SK_TEXT),
            bgcolor=SK_BACKGROUND,
            elevation=0,
        ),
        controls=[content],
    )
```

- [ ] **Step 2: Commit**

```bash
git add src/presentation/pages/student/s_peers_page.py
git commit -m "feat: student peers page"
```

---

## Task 17: Student — Peer Score Page

**Files:**
- Create: `src/presentation/pages/student/s_peer_score_page.py`

- [ ] **Step 1: Crear página de puntuación de criterios**

```python
# src/presentation/pages/student/s_peer_score_page.py
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_SURFACE_ALT, SK_BORDER,
    SK_TEXT, SK_TEXT_FAINT, SK_PRIMARY, CRITERION_COLORS,
)
from src.presentation.components.avatar_circle import avatar_circle
from src.presentation.viewmodels.student_viewmodel import StudentViewModel
from src.domain.models.peer_evaluation import EvalCriterion


def s_peer_score_page(page: ft.Page, vm: StudentViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _criterion_row(criterion: EvalCriterion, color: str, index: int) -> ft.Container:
        score = vm.scores.get(criterion.id, 0)
        level_label = EvalCriterion.level_for(score) if score >= 2 else "Sin puntuar"
        level_text = ft.Text(level_label, size=11, color=color)
        slider = ft.Slider(
            min=2, max=5, divisions=3, value=float(score) if score else 2.0,
            active_color=color, thumb_color=color,
        )

        def _on_change(e) -> None:
            val = int(e.control.value)
            vm.set_score(criterion.id, val)
            level_text.value = EvalCriterion.level_for(val)
            page.update()

        slider.on_change = _on_change

        return ft.Container(
            bgcolor=SK_SURFACE,
            border_radius=14,
            border=ft.border.all(1, SK_BORDER),
            padding=16,
            margin=ft.margin.only(bottom=10),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Container(
                                        width=8, height=8,
                                        bgcolor=color,
                                        border_radius=4,
                                    ),
                                    ft.Text(criterion.label, size=13,
                                           weight=ft.FontWeight.W_600, color=SK_TEXT),
                                ],
                            ),
                            level_text,
                        ],
                    ),
                    slider,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Necesita Mejorar", size=9, color=SK_TEXT_FAINT),
                            ft.Text("Excelente", size=9, color=SK_TEXT_FAINT),
                        ],
                    ),
                ],
            ),
        )

    def _build_body() -> ft.Control:
        peer = vm.current_peer
        if peer is None:
            return ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Text("Selecciona un compañero primero", color=SK_TEXT_FAINT),
            )

        save_btn = ft.ElevatedButton(
            "Guardar evaluación",
            expand=True,
            style=ft.ButtonStyle(bgcolor=SK_PRIMARY, color="#FFFFFF"),
            disabled=not vm.all_criteria_scored,
            on_click=_on_save,
        )

        return ft.Column(
            expand=True,
            controls=[
                ft.Container(
                    padding=16,
                    content=ft.Row(
                        spacing=12,
                        controls=[
                            avatar_circle(peer.initials, size=52, bg_color=SK_PRIMARY),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(peer.name, size=16, weight=ft.FontWeight.W_700, color=SK_TEXT),
                                    ft.Text(
                                        vm.active_eval.name if vm.active_eval else "",
                                        size=12, color=SK_TEXT_FAINT,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.ListView(
                    controls=[
                        _criterion_row(c, CRITERION_COLORS[i], i)
                        for i, c in enumerate(EvalCriterion.DEFAULTS)
                    ],
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=16),
                ),
                ft.Container(padding=16, content=save_btn),
            ],
        )

    def _on_save(_) -> None:
        vm.save_peer_score()
        page.go("/student/peers")

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify
    content.content = _build_body()

    return ft.View(
        route="/student/peer-score",
        bgcolor=SK_BACKGROUND,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/student/peers")),
            title=ft.Text("Evaluar compañero", color=SK_TEXT),
            bgcolor=SK_BACKGROUND,
            elevation=0,
        ),
        controls=[content],
    )
```

- [ ] **Step 2: Commit**

```bash
git add src/presentation/pages/student/s_peer_score_page.py
git commit -m "feat: student peer score page (4 criteria sliders)"
```

---

## Task 18: Student — My Results Page

**Files:**
- Create: `src/presentation/pages/student/s_my_results_page.py`

- [ ] **Step 1: Crear página de mis resultados**

```python
# src/presentation/pages/student/s_my_results_page.py
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    SK_BACKGROUND, SK_SURFACE, SK_BORDER, SK_TEXT, SK_TEXT_MID,
    SK_TEXT_FAINT, SK_PRIMARY, CRITERION_COLORS,
)
from src.presentation.viewmodels.student_viewmodel import StudentViewModel


def s_my_results_page(page: ft.Page, vm: StudentViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _result_bar(label: str, value: float, color: str) -> ft.Container:
        fraction = max(0.0, min(1.0, (value - 2) / 3))
        return ft.Container(
            bgcolor=SK_SURFACE,
            border_radius=12,
            border=ft.border.all(1, SK_BORDER),
            padding=14,
            margin=ft.margin.only(bottom=8),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(label, size=13, weight=ft.FontWeight.W_600, color=SK_TEXT),
                            ft.Text(
                                f"{value:.1f}" if value > 0 else "—",
                                size=13, weight=ft.FontWeight.W_700, color=color,
                            ),
                        ],
                    ),
                    ft.Container(
                        height=6,
                        bgcolor=f"{color}22",
                        border_radius=3,
                        content=ft.Container(
                            height=6,
                            bgcolor=color,
                            border_radius=3,
                            width=None,  # se controla con expand de padre
                            # Flet no soporta "width=fraction*parent_width" directamente,
                            # usar ProgressBar como sustituto:
                        ),
                    ),
                    ft.ProgressBar(value=fraction, bgcolor=f"{color}22", color=color, height=6),
                ],
            ),
        )

    def _build_body() -> ft.Control:
        results = vm.my_results
        ev = vm.active_eval
        avg = vm.my_average
        badge = vm.performance_badge

        visibility_label = ""
        if ev:
            visibility_label = (
                "Resultados visibles" if ev.visibility == "public"
                else "Resultados privados"
            )

        if not results or avg == 0:
            return ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.PENDING_OUTLINED, size=56, color=SK_TEXT_FAINT),
                        ft.Text("Resultados pendientes", color=SK_TEXT_FAINT),
                        ft.Text("Completa tu evaluación para ver tus resultados",
                               size=12, color=SK_TEXT_FAINT, text_align=ft.TextAlign.CENTER),
                    ],
                ),
            )

        avg_color = (
            "#059669" if avg >= 4.0
            else "#7C83D6" if avg >= 3.0
            else "#F59E0B" if avg >= 2.5
            else "#EF4444"
        )

        header = ft.Container(
            bgcolor=SK_PRIMARY,
            border_radius=18,
            padding=20,
            margin=ft.margin.only(bottom=16),
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(badge, size=12, color="#EEEFFE", weight=ft.FontWeight.W_600),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(f"{avg:.2f}", size=48, weight=ft.FontWeight.W_900, color="#FFFFFF"),
                            ft.Text("/5.0", size=16, color="#EEEFFE"),
                        ],
                    ),
                    ft.Text(ev.name if ev else "", size=12, color="#EEEFFE",
                           text_align=ft.TextAlign.CENTER),
                    ft.Text(visibility_label, size=10, color="#EEEFFE80",
                           text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        bars = [
            _result_bar(r.label, r.value, CRITERION_COLORS[i % len(CRITERION_COLORS)])
            for i, r in enumerate(results)
        ]

        return ft.ListView(
            controls=[header, *bars],
            expand=True,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
        )

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify
    content.content = _build_body()

    return ft.View(
        route="/student/results",
        bgcolor=SK_BACKGROUND,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK,
                                 on_click=lambda _: page.go("/student/courses")),
            title=ft.Text("Mis resultados", color=SK_TEXT),
            bgcolor=SK_BACKGROUND,
            elevation=0,
        ),
        controls=[content],
    )
```

- [ ] **Step 2: Commit**

```bash
git add src/presentation/pages/student/s_my_results_page.py
git commit -m "feat: student my-results page"
```

---

## Task 19: Teacher — Dashboard

**Files:**
- Create: `src/presentation/pages/teacher/__init__.py`
- Create: `src/presentation/pages/teacher/t_dash_page.py`

- [ ] **Step 1: Crear dashboard del docente**

```python
# src/presentation/pages/teacher/__init__.py
```

```python
# src/presentation/pages/teacher/t_dash_page.py
"""TDashPage — dashboard del docente."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER,
    TK_TEXT, TK_TEXT_MID, TK_TEXT_FAINT, TK_GOLD, TK_GOLD_LIGHT,
    TK_DANGER, TK_SUCCESS, TK_WARNING,
)
from src.presentation.components.avatar_circle import avatar_circle
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def t_dash_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _stat_card(label: str, value: str, color: str) -> ft.Container:
        return ft.Container(
            bgcolor=TK_SURFACE,
            border_radius=14,
            border=ft.border.all(1, TK_BORDER),
            padding=14,
            expand=True,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(value, size=28, weight=ft.FontWeight.W_900, color=color),
                    ft.Text(label, size=11, color=TK_TEXT_FAINT),
                ],
            ),
        )

    def _eval_card(ev) -> ft.Container:
        active_label = "Activa" if ev.is_active else "Cerrada"
        active_color = TK_SUCCESS if ev.is_active else TK_TEXT_FAINT

        def _results(_) -> None:
            vm.load_group_results(ev)
            page.go("/teacher/results")

        def _rename(_) -> None:
            name_field = ft.TextField(value=ev.name, label="Nuevo nombre")

            def _confirm(_) -> None:
                try:
                    vm.rename_evaluation(ev.id, name_field.value or ev.name)
                    page.close(dlg)
                except Exception as e:
                    name_field.error_text = str(e)
                    page.update()

            dlg = ft.AlertDialog(
                title=ft.Text("Renombrar evaluación"),
                content=name_field,
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.close(dlg)),
                    ft.ElevatedButton("Guardar", on_click=_confirm),
                ],
            )
            page.open(dlg)

        def _delete(_) -> None:
            def _confirm(_) -> None:
                vm.delete_evaluation(ev.id)
                page.close(dlg)

            dlg = ft.AlertDialog(
                title=ft.Text("¿Eliminar evaluación?"),
                content=ft.Text(f"Se eliminará '{ev.name}' y todas sus respuestas."),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.close(dlg)),
                    ft.ElevatedButton(
                        "Eliminar",
                        style=ft.ButtonStyle(bgcolor=TK_DANGER, color="#FFFFFF"),
                        on_click=_confirm,
                    ),
                ],
            )
            page.open(dlg)

        return ft.Container(
            bgcolor=TK_SURFACE,
            border_radius=14,
            border=ft.border.all(1, TK_BORDER),
            padding=14,
            margin=ft.margin.only(bottom=8),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                expand=True,
                                spacing=2,
                                controls=[
                                    ft.Text(ev.name, size=14, weight=ft.FontWeight.W_600, color=TK_TEXT),
                                    ft.Text(ev.course_name or ev.category_name, size=11, color=TK_TEXT_FAINT),
                                ],
                            ),
                            ft.Container(
                                bgcolor=f"{active_color}22",
                                border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                content=ft.Text(active_label, size=10, color=active_color,
                                               weight=ft.FontWeight.W_600),
                            ),
                        ]
                    ),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.TextButton("Resultados", on_click=_results),
                            ft.TextButton("Renombrar",  on_click=_rename),
                            ft.TextButton(
                                "Eliminar",
                                style=ft.ButtonStyle(color=TK_DANGER),
                                on_click=_delete,
                            ),
                        ],
                    ),
                ],
            ),
        )

    def _profile_sheet() -> ft.BottomSheet:
        t = vm.teacher
        initials = t.initials if t else "?"
        name     = t.name    if t else ""
        email    = t.email   if t else ""

        def _logout(_) -> None:
            page.close(bs)
            def _do():
                vm.logout()
                page.go("/login")
            page.run_thread(_do)

        bs = ft.BottomSheet(
            open=True,
            content=ft.Container(
                padding=24,
                bgcolor=TK_SURFACE,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.Row(
                            spacing=12,
                            controls=[
                                avatar_circle(initials, size=48, bg_color=TK_GOLD, text_color=TK_BACKGROUND),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(name, size=16, weight=ft.FontWeight.W_600, color=TK_TEXT),
                                        ft.Text(email, size=12, color=TK_TEXT_FAINT),
                                    ],
                                ),
                            ],
                        ),
                        ft.Divider(color=TK_BORDER),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.LOGOUT, color=TK_DANGER),
                            title=ft.Text("Cerrar sesión", color=TK_DANGER),
                            on_click=_logout,
                        ),
                    ],
                ),
            ),
        )
        return bs

    def _build_body() -> ft.Control:
        if vm.is_loading:
            return ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.ProgressRing(color=TK_GOLD),
            )
        active_count = sum(1 for e in vm.evaluations if e.is_active)
        closed_count = len(vm.evaluations) - active_count
        evals = vm.evaluations

        stats_row = ft.Row(
            spacing=8,
            controls=[
                _stat_card("Evaluaciones", str(len(evals)), TK_GOLD),
                _stat_card("Activas", str(active_count), TK_SUCCESS),
                _stat_card("Grupos", str(vm.total_groups), TK_TEXT_MID),
            ],
        )

        items: list[ft.Control] = [
            stats_row,
            ft.Container(height=8),
        ]
        if evals:
            items.append(
                ft.Text("EVALUACIONES", size=10, color=TK_TEXT_FAINT,
                       weight=ft.FontWeight.W_600, letter_spacing=1.2)
            )
            items.extend(_eval_card(e) for e in evals)

        return ft.ListView(
            controls=items,
            expand=True,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify

    page.run_thread(lambda: (vm.check_session() if not vm.is_logged_in else _notify()))
    content.content = _build_body()

    nav = ft.NavigationBar(
        bgcolor=TK_SURFACE,
        indicator_color=TK_GOLD_LIGHT,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_OUTLINED, label="Inicio"),
            ft.NavigationBarDestination(icon=ft.Icons.UPLOAD_FILE_OUTLINED, label="Importar"),
            ft.NavigationBarDestination(icon=ft.Icons.BOOK_OUTLINED, label="Cursos"),
        ],
        on_change=lambda e: [
            page.go("/teacher/dash"),
            page.go("/teacher/profile"),
            page.go("/teacher/courses"),
        ][e.control.selected_index],
    )

    return ft.View(
        route="/teacher/dash",
        bgcolor=TK_BACKGROUND,
        appbar=ft.AppBar(
            title=ft.Text("Dashboard", color=TK_TEXT),
            bgcolor=TK_BACKGROUND,
            elevation=0,
            actions=[
                ft.IconButton(
                    ft.Icons.ADD_CIRCLE_OUTLINE,
                    icon_color=TK_GOLD,
                    tooltip="Nueva evaluación",
                    on_click=lambda _: page.go("/teacher/new-eval"),
                ),
                ft.IconButton(
                    ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
                    tooltip="Perfil",
                    on_click=lambda _: page.open(_profile_sheet()),
                ),
            ],
        ),
        navigation_bar=nav,
        controls=[content],
    )
```

- [ ] **Step 2: Commit**

```bash
git add src/presentation/pages/teacher/
git commit -m "feat: teacher dashboard page"
```

---

## Task 20: Teacher — Import Page

**Files:**
- Create: `src/presentation/pages/teacher/t_import_page.py`

- [ ] **Step 1: Crear página de importación CSV**

```python
# src/presentation/pages/teacher/t_import_page.py
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER,
    TK_TEXT, TK_TEXT_FAINT, TK_GOLD, TK_DANGER, TK_SUCCESS,
)
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def t_import_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content        = ft.Container(expand=True)
    pending_csv    = {"content": None, "filename": ""}
    selected_course_id   = {"v": None}
    category_name_field  = ft.TextField(
        label="Nombre de la categoría de grupos",
        hint_text="Ej: Sprint 1",
    )
    error_text = ft.Text("", color=TK_DANGER, size=12, visible=False)
    success_text = ft.Text("", color=TK_SUCCESS, size=12, visible=False)

    file_picker = ft.FilePicker(
        on_result=lambda e: _on_file_picked(e),
    )
    page.overlay.append(file_picker)
    page.update()

    def _on_file_picked(e: ft.FilePickerResultEvent) -> None:
        if not e.files:
            return
        f = e.files[0]
        pending_csv["filename"] = f.name
        try:
            with open(f.path, "r", encoding="utf-8-sig") as fh:
                pending_csv["content"] = fh.read()
        except Exception as ex:
            error_text.value   = f"Error leyendo archivo: {ex}"
            error_text.visible = True
            page.update()
            return
        _refresh_import_section()

    def _course_picker_sheet() -> ft.BottomSheet:
        def _pick(course_id: int, name: str) -> None:
            selected_course_id["v"] = course_id
            _refresh_import_section()
            page.close(bs)

        def _create_new(_) -> None:
            name_f = ft.TextField(label="Nombre del curso")
            code_f = ft.TextField(label="Código (opcional)")

            def _do_create(_) -> None:
                if not name_f.value:
                    return
                vm.create_course(name_f.value, code_f.value or "")
                page.close(create_dlg)
                page.close(bs)

            create_dlg = ft.AlertDialog(
                title=ft.Text("Nuevo curso"),
                content=ft.Column(tight=True, controls=[name_f, code_f]),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.close(create_dlg)),
                    ft.ElevatedButton("Crear", on_click=_do_create),
                ],
            )
            page.open(create_dlg)

        course_tiles = [
            ft.ListTile(
                title=ft.Text(c.name, color=TK_TEXT),
                subtitle=ft.Text(c.code, color=TK_TEXT_FAINT) if c.code else None,
                on_click=lambda _, cid=c.id, cname=c.name: _pick(cid, cname),
            )
            for c in vm.courses
        ]

        bs = ft.BottomSheet(
            open=True,
            content=ft.Container(
                bgcolor=TK_SURFACE,
                padding=16,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Text("Selecciona un curso", size=16,
                               weight=ft.FontWeight.W_700, color=TK_TEXT),
                        ft.Divider(color=TK_BORDER),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.ADD, color=TK_GOLD),
                            title=ft.Text("Crear nuevo curso", color=TK_GOLD),
                            on_click=_create_new,
                        ),
                        *course_tiles,
                    ],
                ),
            ),
        )
        return bs

    def _do_import() -> None:
        csv_content = pending_csv["content"]
        cat_name    = category_name_field.value or ""
        course_id   = selected_course_id["v"]
        if not csv_content:
            error_text.value   = "Selecciona un archivo CSV primero"
            error_text.visible = True
            page.update()
            return
        if not cat_name.strip():
            error_text.value   = "Ingresa un nombre de categoría"
            error_text.visible = True
            page.update()
            return
        if course_id is None:
            error_text.value   = "Selecciona un curso"
            error_text.visible = True
            page.update()
            return

        def _run() -> None:
            vm.import_csv(csv_content, cat_name, course_id)
            if vm.import_error:
                error_text.value   = vm.import_error
                error_text.visible = True
            else:
                success_text.value   = f"Categoría '{cat_name}' importada correctamente"
                success_text.visible = True
                pending_csv["content"]  = None
                pending_csv["filename"] = ""
                selected_course_id["v"] = None
                category_name_field.value = ""
            page.update()

        page.run_thread(_run)

    def _refresh_import_section() -> None:
        content.content = _build_body()
        page.update()

    def _build_category_tile(cat) -> ft.Container:
        def _delete(_) -> None:
            dlg = ft.AlertDialog(
                title=ft.Text("¿Eliminar categoría?"),
                content=ft.Text(f"'{cat.name}' y todos sus grupos serán eliminados."),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.close(dlg)),
                    ft.ElevatedButton(
                        "Eliminar",
                        style=ft.ButtonStyle(bgcolor=TK_DANGER, color="#FFFFFF"),
                        on_click=lambda _: (vm.delete_category(cat.id), page.close(dlg)),
                    ),
                ],
            )
            page.open(dlg)

        return ft.Container(
            bgcolor=TK_SURFACE,
            border_radius=12,
            border=ft.border.all(1, TK_BORDER),
            padding=12,
            margin=ft.margin.only(bottom=8),
            content=ft.Row(
                controls=[
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(cat.name, size=13, weight=ft.FontWeight.W_600, color=TK_TEXT),
                            ft.Text(
                                f"{cat.group_count} grupos · {cat.member_count} miembros",
                                size=11, color=TK_TEXT_FAINT,
                            ),
                        ],
                    ),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=TK_DANGER, on_click=_delete),
                ]
            ),
        )

    def _build_body() -> ft.Control:
        filename = pending_csv["filename"]
        course_name = ""
        if selected_course_id["v"] is not None:
            c = next((c for c in vm.courses if c.id == selected_course_id["v"]), None)
            course_name = c.name if c else ""

        import_section = ft.Column(
            spacing=10,
            controls=[
                ft.Text("IMPORTAR GRUPOS", size=10, weight=ft.FontWeight.W_600,
                       color=TK_TEXT_FAINT, letter_spacing=1.2),
                ft.Container(
                    bgcolor=TK_SURFACE,
                    border_radius=14,
                    border=ft.border.all(1, TK_BORDER),
                    padding=16,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.ElevatedButton(
                                f"📄 {filename}" if filename else "Seleccionar CSV",
                                style=ft.ButtonStyle(
                                    bgcolor=TK_GOLD if filename else TK_SURFACE_ALT,
                                    color=TK_BACKGROUND if filename else TK_TEXT,
                                ),
                                on_click=lambda _: file_picker.pick_files(
                                    allowed_extensions=["csv"],
                                    allow_multiple=False,
                                ),
                            ),
                            ft.ElevatedButton(
                                f"📚 {course_name}" if course_name else "Seleccionar curso",
                                style=ft.ButtonStyle(
                                    bgcolor=TK_GOLD if course_name else TK_SURFACE_ALT,
                                    color=TK_BACKGROUND if course_name else TK_TEXT,
                                ),
                                on_click=lambda _: page.open(_course_picker_sheet()),
                            ),
                            category_name_field,
                            error_text,
                            success_text,
                            ft.ElevatedButton(
                                "Importar" if not vm.import_loading else "Importando...",
                                disabled=vm.import_loading,
                                style=ft.ButtonStyle(bgcolor=TK_GOLD, color=TK_BACKGROUND),
                                expand=True,
                                on_click=lambda _: _do_import(),
                            ),
                        ],
                    ),
                ),
            ],
        )

        categories_section = ft.Column(
            spacing=8,
            controls=[
                ft.Container(height=16),
                ft.Text("CATEGORÍAS IMPORTADAS", size=10, weight=ft.FontWeight.W_600,
                       color=TK_TEXT_FAINT, letter_spacing=1.2),
                *(
                    [ft.Text("Sin categorías importadas", color=TK_TEXT_FAINT, size=12)]
                    if not vm.categories
                    else [_build_category_tile(c) for c in vm.categories]
                ),
            ],
        )

        return ft.ListView(
            controls=[import_section, categories_section],
            expand=True,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify
    content.content = _build_body()

    return ft.View(
        route="/teacher/import",
        bgcolor=TK_BACKGROUND,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK,
                                 on_click=lambda _: page.go("/teacher/dash")),
            title=ft.Text("Importar grupos", color=TK_TEXT),
            bgcolor=TK_BACKGROUND,
            elevation=0,
        ),
        controls=[content],
    )
```

- [ ] **Step 2: Commit**

```bash
git add src/presentation/pages/teacher/t_import_page.py
git commit -m "feat: teacher import page (CSV + course picker)"
```

---

## Task 21: Teacher — New Eval Page

**Files:**
- Create: `src/presentation/pages/teacher/t_new_eval_page.py`

- [ ] **Step 1: Crear formulario de nueva evaluación**

```python
# src/presentation/pages/teacher/t_new_eval_page.py
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER,
    TK_TEXT, TK_TEXT_FAINT, TK_GOLD, TK_DANGER,
)
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def t_new_eval_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content = ft.Container(expand=True)

    name_field = ft.TextField(
        label="Nombre de la evaluación",
        value=vm.eval_name,
        on_change=lambda e: setattr(vm, "eval_name", e.control.value),
    )
    error_text = ft.Text("", color=TK_DANGER, size=12, visible=False)

    HOUR_OPTIONS = [24, 48, 72, 96, 120, 168]
    VISIBILITY_OPTIONS = [("Privada", "private"), ("Pública", "public")]

    def _hours_chips() -> ft.Row:
        chips = []
        for h in HOUR_OPTIONS:
            selected = vm.selected_hours == h
            def _pick(_, hours=h):
                vm.selected_hours = hours
                _refresh()
            chips.append(
                ft.Container(
                    on_click=_pick,
                    bgcolor=TK_GOLD if selected else TK_SURFACE_ALT,
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    content=ft.Text(
                        f"{h}h", size=12, color=TK_BACKGROUND if selected else TK_TEXT_FAINT,
                        weight=ft.FontWeight.W_600,
                    ),
                )
            )
        return ft.Row(wrap=True, spacing=6, controls=chips)

    def _visibility_chips() -> ft.Row:
        chips = []
        for label, val in VISIBILITY_OPTIONS:
            selected = vm.selected_visibility == val
            def _pick(_, v=val):
                vm.selected_visibility = v
                _refresh()
            chips.append(
                ft.Container(
                    on_click=_pick,
                    bgcolor=TK_GOLD if selected else TK_SURFACE_ALT,
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    content=ft.Text(
                        label, size=12,
                        color=TK_BACKGROUND if selected else TK_TEXT_FAINT,
                        weight=ft.FontWeight.W_600,
                    ),
                )
            )
        return ft.Row(spacing=8, controls=chips)

    def _course_picker_sheet() -> ft.BottomSheet:
        def _pick(_, cid, cname):
            vm.selected_course_id   = cid
            vm.selected_course_name = cname
            vm.load_categories_for_course(cid)
            page.close(bs)
            _refresh()

        tiles = [
            ft.ListTile(
                title=ft.Text(c.name, color=TK_TEXT),
                on_click=lambda e, cid=c.id, cname=c.name: _pick(e, cid, cname),
            )
            for c in vm.courses
        ]
        bs = ft.BottomSheet(
            open=True,
            content=ft.Container(
                bgcolor=TK_SURFACE, padding=16,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Text("Selecciona un curso", size=16, weight=ft.FontWeight.W_700, color=TK_TEXT),
                        ft.Divider(color=TK_BORDER),
                        *tiles,
                    ],
                ),
            ),
        )
        return bs

    def _category_picker_sheet() -> ft.BottomSheet:
        def _pick(_, cid, cname):
            vm.selected_category_id   = cid
            vm.selected_category_name = cname
            page.close(bs)
            _refresh()

        cats = vm.categories_for_course
        tiles = [
            ft.ListTile(
                title=ft.Text(c.name, color=TK_TEXT),
                subtitle=ft.Text(
                    f"{c.group_count} grupos · {c.member_count} miembros",
                    color=TK_TEXT_FAINT, size=11,
                ),
                on_click=lambda e, cid=c.id, cname=c.name: _pick(e, cid, cname),
            )
            for c in cats
        ]
        empty = [ft.Text("No hay categorías para este curso", color=TK_TEXT_FAINT)] if not cats else []
        bs = ft.BottomSheet(
            open=True,
            content=ft.Container(
                bgcolor=TK_SURFACE, padding=16,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Text("Selecciona categoría de grupos", size=16,
                               weight=ft.FontWeight.W_700, color=TK_TEXT),
                        ft.Divider(color=TK_BORDER),
                        *empty,
                        *tiles,
                    ],
                ),
            ),
        )
        return bs

    def _build_body() -> ft.Control:
        course_btn = ft.ElevatedButton(
            vm.selected_course_name or "Seleccionar curso",
            style=ft.ButtonStyle(
                bgcolor=TK_GOLD if vm.selected_course_name else TK_SURFACE_ALT,
                color=TK_BACKGROUND if vm.selected_course_name else TK_TEXT,
            ),
            on_click=lambda _: page.open(_course_picker_sheet()),
            expand=True,
        )
        cat_btn = ft.ElevatedButton(
            vm.selected_category_name or "Seleccionar categoría",
            style=ft.ButtonStyle(
                bgcolor=TK_GOLD if vm.selected_category_name else TK_SURFACE_ALT,
                color=TK_BACKGROUND if vm.selected_category_name else TK_TEXT,
            ),
            on_click=lambda _: page.open(_category_picker_sheet()),
            expand=True,
            disabled=vm.selected_course_id is None,
        )
        create_btn = ft.ElevatedButton(
            "Crear evaluación" if not vm.is_loading else "Creando...",
            style=ft.ButtonStyle(bgcolor=TK_GOLD, color=TK_BACKGROUND),
            expand=True,
            disabled=vm.is_loading,
            on_click=_on_create,
        )

        return ft.ListView(
            controls=[
                ft.Text("NUEVA EVALUACIÓN", size=10, weight=ft.FontWeight.W_600,
                       color=TK_TEXT_FAINT, letter_spacing=1.2),
                ft.Container(height=8),
                name_field,
                ft.Container(height=8),
                ft.Text("Curso", size=12, color=TK_TEXT_FAINT),
                course_btn,
                ft.Container(height=8),
                ft.Text("Grupos", size=12, color=TK_TEXT_FAINT),
                cat_btn,
                ft.Container(height=8),
                ft.Text("Duración", size=12, color=TK_TEXT_FAINT),
                _hours_chips(),
                ft.Container(height=8),
                ft.Text("Visibilidad de resultados", size=12, color=TK_TEXT_FAINT),
                _visibility_chips(),
                ft.Container(height=16),
                error_text,
                create_btn,
            ],
            expand=True,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )

    def _on_create(_) -> None:
        vm.eval_name = name_field.value or ""
        def _run() -> None:
            err = vm.create_evaluation()
            if err:
                error_text.value   = err
                error_text.visible = True
                page.update()
            else:
                page.go("/teacher/dash")
        page.run_thread(_run)

    def _refresh() -> None:
        content.content = _build_body()
        page.update()

    def _notify() -> None:
        _refresh()

    vm._notify = _notify
    content.content = _build_body()

    return ft.View(
        route="/teacher/new-eval",
        bgcolor=TK_BACKGROUND,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK,
                                 on_click=lambda _: page.go("/teacher/dash")),
            title=ft.Text("Nueva evaluación", color=TK_TEXT),
            bgcolor=TK_BACKGROUND,
            elevation=0,
        ),
        controls=[content],
    )
```

- [ ] **Step 2: Commit**

```bash
git add src/presentation/pages/teacher/t_new_eval_page.py
git commit -m "feat: teacher new-eval page"
```

---

## Task 22: Teacher — Results Page

**Files:**
- Create: `src/presentation/pages/teacher/t_results_page.py`

- [ ] **Step 1: Crear página de resultados grupales**

```python
# src/presentation/pages/teacher/t_results_page.py
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER,
    TK_TEXT, TK_TEXT_FAINT, TK_GOLD, TK_SUCCESS, TK_WARNING, TK_DANGER,
    CRITERION_COLORS_DARK,
)
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def t_results_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content = ft.Container(expand=True)

    CRITERION_LABELS = ["PUNTU", "CONTRIB", "COMPRO", "ACTITU"]

    def _score_color(score: float) -> str:
        if score >= 4.0:
            return TK_SUCCESS
        if score >= 3.0:
            return TK_GOLD
        if score >= 2.5:
            return TK_WARNING
        return TK_DANGER

    def _group_card(group, index: int) -> ft.Container:
        color = _score_color(group.average)

        def _on_drill(_) -> None:
            vm.drill_group_index = index
            content.content = _build_drill(group)
            page.update()

        criteria_bars = ft.Row(
            spacing=4,
            controls=[
                ft.Container(
                    expand=True,
                    height=6,
                    bgcolor=f"{CRITERION_COLORS_DARK[i]}44",
                    border_radius=3,
                    content=ft.Container(
                        expand=True,
                        height=6,
                        bgcolor=CRITERION_COLORS_DARK[i],
                        border_radius=3,
                    ),
                )
                for i, _ in enumerate(group.criteria)
            ],
        )

        return ft.Container(
            bgcolor=TK_SURFACE,
            border_radius=14,
            border=ft.border.all(1, TK_BORDER),
            padding=14,
            margin=ft.margin.only(bottom=8),
            on_click=_on_drill,
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(group.name, size=14, weight=ft.FontWeight.W_600, color=TK_TEXT),
                            ft.Text(
                                f"{group.average:.1f}" if group.average > 0 else "—",
                                size=18, weight=ft.FontWeight.W_900, color=color,
                            ),
                        ],
                    ),
                    ft.Text(
                        f"{len(group.students)} miembros",
                        size=11, color=TK_TEXT_FAINT,
                    ),
                    ft.ProgressBar(
                        value=max(0.0, min(1.0, (group.average - 2) / 3)) if group.average > 0 else 0,
                        bgcolor=f"{color}22",
                        color=color,
                        height=6,
                    ),
                ],
            ),
        )

    def _build_drill(group) -> ft.Control:
        def _back(_) -> None:
            vm.drill_group_index = None
            content.content = _build_overview()
            page.update()

        criterion_rows = [
            ft.Container(
                bgcolor=TK_SURFACE,
                border_radius=12,
                border=ft.border.all(1, TK_BORDER),
                padding=12,
                margin=ft.margin.only(bottom=6),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Container(
                                    width=8, height=8,
                                    bgcolor=CRITERION_COLORS_DARK[i],
                                    border_radius=4,
                                ),
                                ft.Text(CRITERION_LABELS[i], size=12, color=TK_TEXT),
                            ],
                        ),
                        ft.Text(
                            f"{score:.1f}" if score > 0 else "—",
                            size=16, weight=ft.FontWeight.W_700,
                            color=_score_color(score),
                        ),
                    ],
                ),
            )
            for i, score in enumerate(group.criteria)
        ]

        student_rows = [
            ft.Container(
                bgcolor=TK_SURFACE_ALT,
                border_radius=10,
                padding=10,
                margin=ft.margin.only(bottom=4),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(s.name, size=13, color=TK_TEXT),
                        ft.Text(
                            f"{s.score:.1f}" if s.score > 0 else "—",
                            size=13, weight=ft.FontWeight.W_700,
                            color=_score_color(s.score),
                        ),
                    ],
                ),
            )
            for s in group.students
        ]

        return ft.Column(
            expand=True,
            controls=[
                ft.Container(
                    padding=16,
                    content=ft.Row(
                        controls=[
                            ft.IconButton(ft.Icons.ARROW_BACK, on_click=_back, icon_color=TK_TEXT),
                            ft.Column(
                                expand=True,
                                spacing=2,
                                controls=[
                                    ft.Text(group.name, size=16, weight=ft.FontWeight.W_700, color=TK_TEXT),
                                    ft.Text(
                                        f"Promedio: {group.average:.1f}" if group.average > 0 else "Sin datos",
                                        size=12, color=_score_color(group.average),
                                    ),
                                ],
                            ),
                        ]
                    ),
                ),
                ft.ListView(
                    controls=[
                        ft.Text("POR CRITERIO", size=10, color=TK_TEXT_FAINT,
                               weight=ft.FontWeight.W_600, letter_spacing=1.2),
                        *criterion_rows,
                        ft.Container(height=8),
                        ft.Text("POR ESTUDIANTE", size=10, color=TK_TEXT_FAINT,
                               weight=ft.FontWeight.W_600, letter_spacing=1.2),
                        *student_rows,
                    ],
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=16),
                ),
            ],
        )

    def _build_overview() -> ft.Control:
        if vm.results_loading:
            return ft.Container(
                expand=True, alignment=ft.alignment.center,
                content=ft.ProgressRing(color=TK_GOLD),
            )
        groups = vm.group_results
        if not groups:
            return ft.Container(
                expand=True, alignment=ft.alignment.center,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.POLL_OUTLINED, size=56, color=TK_TEXT_FAINT),
                        ft.Text("Sin resultados aún", color=TK_TEXT_FAINT),
                    ],
                ),
            )

        overall = vm.overall_average
        header = ft.Container(
            bgcolor=TK_SURFACE,
            border_radius=18,
            border=ft.border.all(1, TK_BORDER),
            padding=16,
            margin=ft.margin.only(bottom=16),
            content=ft.Column(
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Promedio general", size=11, color=TK_TEXT_FAINT),
                    ft.Text(
                        f"{overall:.2f}" if overall > 0 else "—",
                        size=48, weight=ft.FontWeight.W_900,
                        color=_score_color(overall),
                    ),
                    ft.Text(
                        vm.selected_eval_for_results.name
                        if vm.selected_eval_for_results else "",
                        size=12, color=TK_TEXT_FAINT,
                    ),
                ],
            ),
        )
        return ft.ListView(
            controls=[
                header,
                ft.Text("GRUPOS", size=10, color=TK_TEXT_FAINT,
                       weight=ft.FontWeight.W_600, letter_spacing=1.2),
                *[_group_card(g, i) for i, g in enumerate(groups)],
            ],
            expand=True,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )

    def _build_body() -> ft.Control:
        if vm.drill_group_index is not None and vm.group_results:
            group = vm.group_results[vm.drill_group_index]
            return _build_drill(group)
        return _build_overview()

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify
    content.content = _build_body()

    return ft.View(
        route="/teacher/results",
        bgcolor=TK_BACKGROUND,
        appbar=ft.AppBar(
            leading=ft.IconButton(
                ft.Icons.ARROW_BACK,
                on_click=lambda _: page.go("/teacher/dash"),
            ),
            title=ft.Text("Resultados", color=TK_TEXT),
            bgcolor=TK_BACKGROUND,
            elevation=0,
        ),
        controls=[content],
    )
```

- [ ] **Step 2: Commit**

```bash
git add src/presentation/pages/teacher/t_results_page.py
git commit -m "feat: teacher results page (group drill-down)"
```

---

## Task 23: Teacher — Profile y Course Manage Pages

**Files:**
- Create: `src/presentation/pages/teacher/t_profile_page.py`
- Create: `src/presentation/pages/teacher/t_course_manage_page.py`

- [ ] **Step 1: Crear t_profile_page.py**

```python
# src/presentation/pages/teacher/t_profile_page.py
"""TProfilePage — hub de perfil/importación del docente (tab importar en navbar)."""
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_BORDER, TK_TEXT, TK_TEXT_FAINT,
    TK_GOLD, TK_GOLD_LIGHT, TK_DANGER,
)
from src.presentation.components.avatar_circle import avatar_circle
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def t_profile_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    """Perfil del docente + acceso directo a importar."""
    t = vm.teacher
    initials = t.initials if t else "?"
    name     = t.name    if t else "—"
    email    = t.email   if t else "—"

    def _logout(_) -> None:
        def _do():
            vm.logout()
            page.go("/login")
        page.run_thread(_do)

    nav = ft.NavigationBar(
        bgcolor=TK_SURFACE,
        indicator_color=TK_GOLD_LIGHT,
        selected_index=1,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_OUTLINED, label="Inicio"),
            ft.NavigationBarDestination(icon=ft.Icons.UPLOAD_FILE_OUTLINED, label="Importar"),
            ft.NavigationBarDestination(icon=ft.Icons.BOOK_OUTLINED, label="Cursos"),
        ],
        on_change=lambda e: [
            page.go("/teacher/dash"),
            page.go("/teacher/import"),
            page.go("/teacher/courses"),
        ][e.control.selected_index],
    )

    return ft.View(
        route="/teacher/profile",
        bgcolor=TK_BACKGROUND,
        navigation_bar=nav,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.ListView(
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=16, vertical=24),
                    controls=[
                        ft.Row(
                            spacing=16,
                            controls=[
                                avatar_circle(initials, size=64, bg_color=TK_GOLD, text_color=TK_BACKGROUND),
                                ft.Column(
                                    spacing=4,
                                    controls=[
                                        ft.Text(name, size=18, weight=ft.FontWeight.W_700, color=TK_TEXT),
                                        ft.Text(email, size=12, color=TK_TEXT_FAINT),
                                        ft.Container(
                                            bgcolor=TK_GOLD_LIGHT,
                                            border_radius=6,
                                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                            content=ft.Text("Docente", size=10, color=TK_GOLD,
                                                           weight=ft.FontWeight.W_600),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        ft.Divider(color=TK_BORDER, height=32),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.UPLOAD_FILE_OUTLINED, color=TK_GOLD),
                            title=ft.Text("Importar grupos CSV", color=TK_TEXT),
                            subtitle=ft.Text("Formato Brightspace", color=TK_TEXT_FAINT, size=11),
                            on_click=lambda _: page.go("/teacher/import"),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.BOOK_OUTLINED, color=TK_GOLD),
                            title=ft.Text("Gestionar cursos", color=TK_TEXT),
                            on_click=lambda _: page.go("/teacher/courses"),
                        ),
                        ft.Divider(color=TK_BORDER),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.LOGOUT, color=TK_DANGER),
                            title=ft.Text("Cerrar sesión", color=TK_DANGER),
                            on_click=_logout,
                        ),
                    ],
                ),
            )
        ],
    )
```

- [ ] **Step 2: Crear t_course_manage_page.py**

```python
# src/presentation/pages/teacher/t_course_manage_page.py
from __future__ import annotations
import flet as ft
from src.presentation.theme.app_colors import (
    TK_BACKGROUND, TK_SURFACE, TK_SURFACE_ALT, TK_BORDER,
    TK_TEXT, TK_TEXT_FAINT, TK_GOLD, TK_GOLD_LIGHT, TK_DANGER,
)
from src.presentation.viewmodels.teacher_viewmodel import TeacherViewModel


def t_course_manage_page(page: ft.Page, vm: TeacherViewModel) -> ft.View:
    content = ft.Container(expand=True)

    def _course_tile(course) -> ft.Container:
        def _delete(_) -> None:
            dlg = ft.AlertDialog(
                title=ft.Text("¿Eliminar curso?"),
                content=ft.Text(f"'{course.name}' será eliminado."),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.close(dlg)),
                    ft.ElevatedButton(
                        "Eliminar",
                        style=ft.ButtonStyle(bgcolor=TK_DANGER, color="#FFFFFF"),
                        on_click=lambda _: (vm.delete_course(course.id), page.close(dlg)),
                    ),
                ],
            )
            page.open(dlg)

        return ft.Container(
            bgcolor=TK_SURFACE,
            border_radius=12,
            border=ft.border.all(1, TK_BORDER),
            padding=14,
            margin=ft.margin.only(bottom=8),
            content=ft.Row(
                controls=[
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(course.name, size=14, weight=ft.FontWeight.W_600, color=TK_TEXT),
                            ft.Text(course.code or "Sin código", size=11, color=TK_TEXT_FAINT),
                        ],
                    ),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=TK_DANGER, on_click=_delete),
                ]
            ),
        )

    def _add_course_dialog() -> ft.AlertDialog:
        name_f = ft.TextField(label="Nombre del curso", autofocus=True)
        code_f = ft.TextField(label="Código (opcional)")

        def _create(_) -> None:
            if not name_f.value:
                name_f.error_text = "Requerido"
                page.update()
                return
            vm.create_course(name_f.value, code_f.value or "")
            page.close(dlg)

        dlg = ft.AlertDialog(
            title=ft.Text("Nuevo curso"),
            content=ft.Column(tight=True, controls=[name_f, code_f]),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.close(dlg)),
                ft.ElevatedButton("Crear", on_click=_create,
                                 style=ft.ButtonStyle(bgcolor=TK_GOLD, color=TK_BACKGROUND)),
            ],
        )
        return dlg

    def _build_body() -> ft.Control:
        if vm.is_loading:
            return ft.Container(
                expand=True, alignment=ft.alignment.center,
                content=ft.ProgressRing(color=TK_GOLD),
            )
        courses = vm.courses
        if not courses:
            return ft.Container(
                expand=True, alignment=ft.alignment.center,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.BOOK_OUTLINED, size=56, color=TK_TEXT_FAINT),
                        ft.Text("Sin cursos. Crea el primero.", color=TK_TEXT_FAINT),
                    ],
                ),
            )
        return ft.ListView(
            controls=[_course_tile(c) for c in courses],
            expand=True,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )

    def _notify() -> None:
        content.content = _build_body()
        page.update()

    vm._notify = _notify
    content.content = _build_body()

    nav = ft.NavigationBar(
        bgcolor=TK_SURFACE,
        indicator_color=TK_GOLD_LIGHT,
        selected_index=2,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_OUTLINED, label="Inicio"),
            ft.NavigationBarDestination(icon=ft.Icons.UPLOAD_FILE_OUTLINED, label="Importar"),
            ft.NavigationBarDestination(icon=ft.Icons.BOOK_OUTLINED, label="Cursos"),
        ],
        on_change=lambda e: [
            page.go("/teacher/dash"),
            page.go("/teacher/profile"),
            page.go("/teacher/courses"),
        ][e.control.selected_index],
    )

    return ft.View(
        route="/teacher/courses",
        bgcolor=TK_BACKGROUND,
        navigation_bar=nav,
        appbar=ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK,
                                 on_click=lambda _: page.go("/teacher/dash")),
            title=ft.Text("Cursos", color=TK_TEXT),
            bgcolor=TK_BACKGROUND,
            elevation=0,
            actions=[
                ft.IconButton(
                    ft.Icons.ADD,
                    icon_color=TK_GOLD,
                    tooltip="Nuevo curso",
                    on_click=lambda _: page.open(_add_course_dialog()),
                ),
            ],
        ),
        controls=[content],
    )
```

- [ ] **Step 3: Commit**

```bash
git add src/presentation/pages/teacher/t_profile_page.py \
        src/presentation/pages/teacher/t_course_manage_page.py
git commit -m "feat: teacher profile and course management pages"
```

---

## Task 24: Eliminar código demo y limpiar

**Files:**
- Delete: `src/domain/entities/user.py`
- Delete: `src/domain/repositories/user_repository.py`
- Delete: `src/domain/usecases/get_users.py`
- Delete: `src/data/models/user_model.py`
- Delete: `src/data/datasources/user_local_datasource.py`
- Delete: `src/data/repositories/user_repository_impl.py`
- Delete: `src/presentation/pages/home_page.py`
- Delete: `src/presentation/components/user_card.py`
- Delete: `src/presentation/viewmodels/home_viewmodel.py`
- Modify: `pyproject.toml` (nombre del proyecto)
- Delete: `tests/domain/test_user_entity.py`
- Delete: `tests/domain/test_get_users.py`
- Delete: `tests/data/test_user_model.py`
- Delete: `tests/data/test_user_repository_impl.py`
- Delete: `tests/presentation/test_home_viewmodel.py`

- [ ] **Step 1: Eliminar archivos demo**

```bash
git rm src/domain/entities/user.py \
       src/domain/repositories/user_repository.py \
       src/domain/usecases/get_users.py \
       src/data/models/user_model.py \
       src/data/datasources/user_local_datasource.py \
       src/data/repositories/user_repository_impl.py \
       src/presentation/pages/home_page.py \
       src/presentation/components/user_card.py \
       src/presentation/viewmodels/home_viewmodel.py \
       tests/domain/test_user_entity.py \
       tests/domain/test_get_users.py \
       tests/data/test_user_model.py \
       tests/data/test_user_repository_impl.py \
       tests/presentation/test_home_viewmodel.py
```

- [ ] **Step 2: Actualizar pyproject.toml nombre**

Modificar `pyproject.toml`:
```toml
[project]
name = "evalun"
version = "0.1.0"
description = "Evaluación entre pares — EvalUn (peerUn en Flet)"
requires-python = ">=3.11"
dependencies = ["flet>=0.23.0"]
```

- [ ] **Step 3: Ejecutar todos los tests**

```bash
pytest -v
```
Expected: todos PASS (solo los nuevos tests de peerUn)

- [ ] **Step 4: Ejecutar la app completa**

```bash
python main.py
```
Expected: splash → login → registro/login como estudiante o docente → flujo completo navegable

- [ ] **Step 5: Commit final**

```bash
git add -A
git commit -m "feat: complete peerUn recreation in Flet — clean demo code"
```

---

## Self-Review

### Spec coverage

| Funcionalidad peerUn | Tarea que la implementa |
|---------------------|------------------------|
| Login unificado (docente primero) | Task 4 + Task 12 |
| Registro estudiante/docente | Task 4 + Task 13 |
| Sesiones persistentes (SQLite) | Task 4 |
| SHA-256 passwords | Task 4 |
| CSV Brightspace 7 columnas | Task 5 + Task 20 |
| CRUD cursos | Task 6 + Task 23 |
| CRUD evaluaciones (create/rename/delete) | Task 7 + Task 19 |
| Evaluación activa (hero card) | Task 14 |
| Lista de compañeros + estado | Task 16 |
| Puntuación 4 criterios (2-5) | Task 17 |
| Submit evaluación | Task 16 |
| Mis resultados con promedio | Task 18 |
| Dashboard docente + estadísticas | Task 19 |
| Resultados grupales + drill-down | Task 22 |
| Gestión cursos docente | Task 23 |
| Perfil + logout | Task 14, 19, 23 |
| Tema SK (claro) / TK (oscuro) | Task 8 |
| Paleta SK/TK exacta | Task 8 |
| Splash + restauración de sesión | Task 11 |

### Placeholder scan
Sin `TBD`, `TODO`, `# ...` incompletos, ni referencias a tipos no definidos.

### Type consistency
- `Evaluation.is_active` → `bool` (property, `datetime.now() < closes_at`)
- `StudentViewModel.check_session()` → sincrónico (llama `get_current_session()` sin async)
- `EvalCriterion.DEFAULTS` → `list[EvalCriterion]` (ClassVar)
- `page.run_thread(fn)` → usado en todas las operaciones de DB para no bloquear UI

---

## Execution Handoff

Plan completo guardado en `docs/superpowers/plans/2026-05-02-perun-flet-recreation.md`.

**Dos opciones de ejecución:**

**1. Subagent-Driven (recomendado)** — Se despacha un subagente por tarea, revisión entre tareas, iteración rápida

**2. Inline Execution** — Ejecución en sesión usando executing-plans, con checkpoints

**¿Cuál prefieres?**
