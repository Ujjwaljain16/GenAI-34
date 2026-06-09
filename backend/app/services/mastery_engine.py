"""
Mastery engine — deterministic mastery/retention updates.

Vendored from docs/architecture/mastery_engine.md section 11 (canonical v2.0.0).
Constants are EXACT per the spec (precedence #3); do not change without a spec
version bump. Pure: no I/O. This is one half of the learner-model truth; the
other (scheduling) lives in fsrs.py.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

# --- Constants (exact, per spec) -------------------------------------------
DELTA_CORRECT = 0.10
DELTA_WRONG = -0.08
DELTA_HINT = -0.03
DELTA_SKIP = -0.05
BONUS_LESSON = 0.05
BONUS_QUIZ = 0.08
BONUS_ASSESSMENT = 0.00

RET_CORRECT = 0.07
RET_WRONG = -0.05
RET_HINT = -0.02
RET_SKIP = -0.03
RET_LESSON = 0.04
RET_QUIZ = 0.06
RET_ASSESSMENT = 0.00

DECAY_RATE = 0.995
MASTERY_THRESHOLD = 0.85

MASTERY_MIN, MASTERY_MAX = 0.0, 1.0
RETENTION_MIN, RETENTION_MAX = 0.0, 1.0

MasteryEvent = Literal[
    "correct",
    "wrong",
    "skip",
    "lesson_complete",
    "quiz_complete",
    "assessment_complete",
]
CurriculumAction = Literal[
    "assign_first", "remediate", "continue", "practice", "unlock_dependents"
]


@dataclass
class UpdateResult:
    mastery: float
    retention: float
    mastery_delta: float
    retention_delta: float
    bonus_awarded: bool
    routing: CurriculumAction


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _sanitize(value: float) -> float:
    return value if math.isfinite(value) else 0.0


def get_curriculum_action(mastery: float) -> CurriculumAction:
    if mastery == 0.0:
        return "assign_first"
    if mastery <= 0.30:
        return "remediate"
    if mastery <= 0.60:
        return "continue"
    if mastery < MASTERY_THRESHOLD:
        return "practice"
    return "unlock_dependents"


def apply_login_decay(retention: float, days_since_last_seen: float) -> float:
    """Exponential retention decay; call once per session before event updates."""
    days = max(0.0, days_since_last_seen)
    return clamp(retention * (DECAY_RATE**days))


def update_mastery(
    mastery: float,
    retention: float,
    event: MasteryEvent,
    hint_used: bool = False,
    bonus_eligible: bool = True,
) -> UpdateResult:
    """Apply one learning event; returns new mastery/retention + routing.

    bonus_eligible: for lesson/quiz completion, whether the once-per-version
    completion bonus may be awarded (first completion only).
    """
    mastery = _sanitize(mastery)
    retention = _sanitize(retention)
    m_delta = r_delta = 0.0
    bonus = False

    if event == "correct":
        m_delta = DELTA_CORRECT + (DELTA_HINT if hint_used else 0.0)
        r_delta = RET_CORRECT + (RET_HINT if hint_used else 0.0)
    elif event == "wrong":
        m_delta, r_delta = DELTA_WRONG, RET_WRONG
    elif event == "skip":
        m_delta, r_delta = DELTA_SKIP, RET_SKIP
    elif event == "lesson_complete":
        if bonus_eligible:
            m_delta, r_delta, bonus = BONUS_LESSON, RET_LESSON, True
    elif event == "quiz_complete":
        if bonus_eligible:
            m_delta, r_delta, bonus = BONUS_QUIZ, RET_QUIZ, True
    elif event == "assessment_complete":
        m_delta, r_delta = BONUS_ASSESSMENT, RET_ASSESSMENT
    else:
        raise ValueError(f"Unknown mastery event: {event!r}")

    new_m = clamp(mastery + m_delta, MASTERY_MIN, MASTERY_MAX)
    new_r = clamp(retention + r_delta, RETENTION_MIN, RETENTION_MAX)
    return UpdateResult(
        mastery=new_m,
        retention=new_r,
        mastery_delta=new_m - mastery,
        retention_delta=new_r - retention,
        bonus_awarded=bonus,
        routing=get_curriculum_action(new_m),
    )
