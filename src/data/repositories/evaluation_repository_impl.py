from __future__ import annotations
from datetime import datetime, timedelta
from src.data.services.database_service import DatabaseService
from src.data.utils import build_initials as _build_initials
from src.domain.models.evaluation import Evaluation
from src.domain.models.peer_evaluation import Peer, CriterionResult, EvalCriterion
from src.domain.models.teacher_data import GroupResult, StudentResult
from src.domain.repositories.i_evaluation_repository import IEvaluationRepository


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

    def create(self, name: str, category_id: int, hours: int, visibility: str, teacher_id: int) -> Evaluation:
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
            "INSERT INTO evaluations (name, category_id, hours, visibility, created_at, closes_at, teacher_id) VALUES (?,?,?,?,?,?,?)",
            (name, category_id, hours, visibility, now_ms, closes_ms, teacher_id),
        )
        conn.commit()
        cat_row = conn.execute("SELECT name FROM group_categories WHERE id=?", (category_id,)).fetchone()
        cat_name = cat_row["name"] if cat_row else ""
        return Evaluation(id=cursor.lastrowid, name=name, category_id=category_id,
                         category_name=cat_name, hours=hours, visibility=visibility,
                         created_at=now, closes_at=closes)

    def get_all(self, teacher_id: int) -> list[Evaluation]:
        rows = self._conn().execute(
            """SELECT e.*, gc.name AS category_name, co.name AS course_name
               FROM evaluations e
               JOIN group_categories gc ON gc.id = e.category_id
               LEFT JOIN courses co ON co.id = gc.course_id
               WHERE e.teacher_id = ? ORDER BY e.created_at DESC""",
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
        conn.execute("UPDATE evaluations SET name=? WHERE id=?", (new_name, eval_id))
        conn.commit()

    def delete(self, eval_id: int) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM evaluation_responses WHERE eval_id=?", (eval_id,))
        conn.execute("DELETE FROM evaluations WHERE id=?", (eval_id,))
        conn.commit()

    def get_evaluations_for_student(self, email: str) -> list[Evaluation]:
        rows = self._conn().execute(
            """SELECT DISTINCT e.*, gc.name AS category_name, co.name AS course_name
               FROM evaluations e
               JOIN group_categories gc ON gc.id = e.category_id
               LEFT JOIN courses co ON co.id = gc.course_id
               JOIN groups g ON g.category_id = e.category_id
               JOIN group_members gm ON gm.group_id = g.id
               WHERE LOWER(gm.username) = ? ORDER BY e.created_at DESC""",
            (email.lower(),),
        ).fetchall()
        return [_row_to_eval(dict(r)) for r in rows]

    def get_group_name_for_student(self, eval_id: int, email: str) -> str | None:
        row = self._conn().execute(
            """SELECT g.name FROM groups g
               JOIN group_members gm ON gm.group_id = g.id
               JOIN evaluations e ON e.category_id = g.category_id
               WHERE e.id=? AND LOWER(gm.username)=? LIMIT 1""",
            (eval_id, email.lower()),
        ).fetchone()
        return row["name"] if row else None

    def get_peers_for_student(self, eval_id: int, email: str) -> list[Peer]:
        conn = self._conn()
        grp = conn.execute(
            """SELECT g.id FROM groups g
               JOIN group_members gm ON gm.group_id = g.id
               JOIN evaluations e ON e.category_id = g.category_id
               WHERE e.id=? AND LOWER(gm.username)=? LIMIT 1""",
            (eval_id, email.lower()),
        ).fetchone()
        if grp is None:
            return []
        rows = conn.execute(
            "SELECT * FROM group_members WHERE group_id=? AND LOWER(username)!=?",
            (grp["id"], email.lower()),
        ).fetchall()
        return [Peer(id=str(m["id"]), name=m["name"], initials=_build_initials(m["name"])) for m in rows]

    def save_responses(self, eval_id: int, evaluator_student_id: int, evaluated_member_id: int, scores: dict[str, int]) -> None:
        conn = self._conn()
        for criterion_id, score in scores.items():
            conn.execute(
                "INSERT OR REPLACE INTO evaluation_responses "
                "(eval_id, evaluator_id, evaluated_member_id, criterion_id, score) VALUES (?,?,?,?,?)",
                (eval_id, evaluator_student_id, evaluated_member_id, criterion_id, score),
            )
        conn.commit()

    def has_evaluated(self, eval_id: int, evaluator_student_id: int, evaluated_member_id: int) -> bool:
        row = self._conn().execute(
            "SELECT 1 FROM evaluation_responses WHERE eval_id=? AND evaluator_id=? AND evaluated_member_id=? LIMIT 1",
            (eval_id, evaluator_student_id, evaluated_member_id),
        ).fetchone()
        return row is not None

    def has_completed_all_peers(self, eval_id: int, email: str, student_id: int) -> bool:
        conn = self._conn()
        grp = conn.execute(
            """SELECT g.id FROM groups g
               JOIN group_members gm ON gm.group_id = g.id
               JOIN evaluations e ON e.category_id = g.category_id
               WHERE e.id=? AND LOWER(gm.username)=? LIMIT 1""",
            (eval_id, email.lower()),
        ).fetchone()
        if grp is None:
            return False
        peer_rows = conn.execute(
            "SELECT id FROM group_members WHERE group_id=? AND LOWER(username)!=?",
            (grp["id"], email.lower()),
        ).fetchall()
        total = len(peer_rows)
        if total == 0:
            return False
        peer_ids = [r["id"] for r in peer_rows]
        placeholders = ",".join("?" * len(peer_ids))
        done_row = conn.execute(
            f"SELECT COUNT(DISTINCT evaluated_member_id) AS cnt FROM evaluation_responses WHERE eval_id=? AND evaluator_id=? AND evaluated_member_id IN ({placeholders})",
            (eval_id, student_id, *peer_ids),
        ).fetchone()
        return (done_row["cnt"] if done_row else 0) >= total

    def get_my_results(self, eval_id: int, email: str) -> list[CriterionResult]:
        conn = self._conn()
        member_rows = conn.execute(
            """SELECT gm.id FROM group_members gm
               JOIN groups g ON g.id = gm.group_id
               JOIN evaluations e ON e.category_id = g.category_id
               WHERE e.id=? AND LOWER(gm.username)=?""",
            (eval_id, email.lower()),
        ).fetchall()
        if not member_rows:
            return []
        member_ids = [r["id"] for r in member_rows]
        placeholders = ",".join("?" * len(member_ids))
        rows = conn.execute(
            f"SELECT criterion_id, AVG(CAST(score AS REAL)) AS avg_score FROM evaluation_responses WHERE eval_id=? AND evaluated_member_id IN ({placeholders}) AND score>=2 GROUP BY criterion_id",
            (eval_id, *member_ids),
        ).fetchall()
        avg_map = {r["criterion_id"]: r["avg_score"] for r in rows}
        return [CriterionResult(label=c.label, value=round(avg_map.get(c.id, 0.0), 1)) for c in EvalCriterion.DEFAULTS]

    def get_group_results(self, eval_id: int) -> list[GroupResult]:
        conn = self._conn()
        member_rows = conn.execute(
            """SELECT g.id AS grp_id, g.name AS grp_name, gm.id AS mem_id, gm.name AS mem_name,
                      COALESCE(AVG(CASE WHEN er.score >= 2 THEN CAST(er.score AS REAL) END), 0.0) AS avg_score
               FROM groups g
               JOIN evaluations e ON e.category_id = g.category_id
               JOIN group_members gm ON gm.group_id = g.id
               LEFT JOIN evaluation_responses er ON er.eval_id = e.id AND er.evaluated_member_id = gm.id AND er.score >= 2
               WHERE e.id=?
               GROUP BY g.id, gm.id ORDER BY g.name, gm.name""",
            (eval_id,),
        ).fetchall()
        crit_rows = conn.execute(
            """SELECT g.id AS grp_id, er.criterion_id, AVG(CAST(er.score AS REAL)) AS avg_score
               FROM groups g
               JOIN evaluations e ON e.category_id = g.category_id
               JOIN group_members gm ON gm.group_id = g.id
               JOIN evaluation_responses er ON er.eval_id = e.id AND er.evaluated_member_id = gm.id AND er.score >= 2
               WHERE e.id=?
               GROUP BY g.id, er.criterion_id""",
            (eval_id,),
        ).fetchall()
        crit_map: dict[int, dict[str, float]] = {}
        for r in crit_rows:
            crit_map.setdefault(r["grp_id"], {})[r["criterion_id"]] = r["avg_score"]
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
            students = [StudentResult(initial=m["mem_name"][0].upper() if m["mem_name"] else "?",
                                     name=m["mem_name"], score=round(m["avg_score"], 1)) for m in members]
            cm = crit_map.get(gid, {})
            criteria = [round(cm.get(cid, 0.0), 1) for cid in CRITERION_IDS]
            valid = [s.score for s in students if s.score > 0]
            average = round(sum(valid) / len(valid), 1) if valid else 0.0
            results.append(GroupResult(name=gname, average=average, criteria=criteria, students=students))
        return results
