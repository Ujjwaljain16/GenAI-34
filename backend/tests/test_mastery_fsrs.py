"""Unit tests for the deterministic mastery engine + FSRS scheduler."""
import math

from app.services import mastery_engine as me
from app.services import fsrs


# --- mastery engine (constants are exact per spec) -------------------------

def test_correct_delta():
    r = me.update_mastery(0.60, 0.70, "correct")
    assert math.isclose(r.mastery, 0.70, abs_tol=1e-9)
    assert math.isclose(r.retention, 0.77, abs_tol=1e-9)


def test_correct_with_hint_is_smaller():
    r = me.update_mastery(0.60, 0.70, "correct", hint_used=True)
    assert math.isclose(r.mastery, 0.67, abs_tol=1e-9)   # 0.10 - 0.03


def test_wrong_and_clamp_floor():
    assert me.update_mastery(0.0, 0.0, "wrong").mastery == 0.0   # clamped at 0


def test_ceiling_clamp():
    assert me.update_mastery(0.95, 0.95, "correct").mastery == 1.0


def test_lesson_bonus_once():
    first = me.update_mastery(0.5, 0.5, "lesson_complete", bonus_eligible=True)
    assert math.isclose(first.mastery, 0.55, abs_tol=1e-9)
    replay = me.update_mastery(0.5, 0.5, "lesson_complete", bonus_eligible=False)
    assert replay.mastery == 0.5   # no bonus on replay


def test_routing_thresholds():
    assert me.get_curriculum_action(0.0) == "assign_first"
    assert me.get_curriculum_action(0.2) == "remediate"
    assert me.get_curriculum_action(0.5) == "continue"
    assert me.get_curriculum_action(0.8) == "practice"
    assert me.get_curriculum_action(0.9) == "unlock_dependents"


def test_login_decay():
    assert me.apply_login_decay(1.0, 0) == 1.0
    assert me.apply_login_decay(1.0, 10) < 1.0


# --- FSRS scheduler --------------------------------------------------------

def test_good_review_grows_interval():
    s0 = fsrs.init_state()
    s1, i1 = fsrs.review(s0, fsrs.GRADE_GOOD)
    s2, i2 = fsrs.review(s1, fsrs.GRADE_GOOD)
    assert i2 > i1                       # intervals expand on repeated success
    assert s2.repetitions == 2


def test_again_resets_stability_and_counts_lapse():
    s0, _ = fsrs.review(fsrs.init_state(), fsrs.GRADE_EASY)
    s1, interval = fsrs.review(s0, fsrs.GRADE_AGAIN)
    assert s1.stability == fsrs.DEFAULT_STABILITY
    assert s1.lapses == 1
    assert s1.repetitions == 0
    assert interval >= 1


def test_difficulty_bounds():
    s = fsrs.init_state()
    for _ in range(20):
        s, _ = fsrs.review(s, fsrs.GRADE_AGAIN)   # repeatedly hard
    assert 1.0 <= s.difficulty <= 10.0


def test_retrievability_decreases_with_time():
    assert fsrs.retrievability(5.0, 0) > fsrs.retrievability(5.0, 30)


def test_bad_grade_rejected():
    try:
        fsrs.review(fsrs.init_state(), 7)
        assert False
    except ValueError:
        pass
