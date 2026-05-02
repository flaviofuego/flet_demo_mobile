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


def test_eval_criterion_defaults_has_4_criteria():
    assert len(EvalCriterion.DEFAULTS) == 4
    ids = [c.id for c in EvalCriterion.DEFAULTS]
    assert "punct" in ids
    assert "contrib" in ids
    assert "commit" in ids
    assert "attitude" in ids


def test_group_category_counts():
    from src.domain.models.group_category import GroupCategory, CourseGroup, GroupMember
    cat = GroupCategory(
        id=1, name="Sprint 1",
        imported_at=datetime.now(),
        groups=[
            CourseGroup(id=1, name="G1", members=[
                GroupMember(id=1, name="Ana", username="ana@uni.edu"),
                GroupMember(id=2, name="Bob", username="bob@uni.edu"),
            ]),
            CourseGroup(id=2, name="G2", members=[
                GroupMember(id=3, name="Carlos", username="carlos@uni.edu"),
            ]),
        ]
    )
    assert cat.group_count == 2
    assert cat.member_count == 3
