"""
Spaced-repetition scheduler (System Design Section G).

A compact, deterministic FSRS-style scheduler matching the concept_fsrs schema
(stability, difficulty, retrievability, repetitions, lapses, next_due). Grades
follow the FSRS convention: 1=Again, 2=Hard, 3=Good, 4=Easy.

Pure: no I/O. Stability drives the review interval (days until ~90% recall);
successful reviews grow it, lapses reset it. Retrievability is the forgetting
curve used to sort revision urgency.
"""
from __future__ import annotations

from dataclasses import dataclass

DEFAULT_STABILITY = 0.4
DEFAULT_DIFFICULTY = 5.0

GRADE_AGAIN, GRADE_HARD, GRADE_GOOD, GRADE_EASY = 1, 2, 3, 4


@dataclass
class FsrsState:
    stability: float = DEFAULT_STABILITY
    difficulty: float = DEFAULT_DIFFICULTY
    retrievability: float = 1.0
    repetitions: int = 0
    lapses: int = 0


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def retrievability(stability: float, elapsed_days: float) -> float:
    """FSRS forgetting curve: probability of recall after `elapsed_days`."""
    s = max(0.01, stability)
    return _clamp((1.0 + max(0.0, elapsed_days) / (9.0 * s)) ** -1.0, 0.0, 1.0)


def interval_days(stability: float) -> int:
    """Days until the next review (target ~90% retention)."""
    return max(1, round(stability))


def init_state() -> FsrsState:
    return FsrsState()


def review(state: FsrsState, grade: int) -> tuple[FsrsState, int]:
    """Apply a review grade. Returns (new_state, interval_days)."""
    if grade not in (GRADE_AGAIN, GRADE_HARD, GRADE_GOOD, GRADE_EASY):
        raise ValueError(f"grade must be 1-4, got {grade}")

    # Difficulty: harder grades raise difficulty, easier grades lower it.
    new_d = _clamp(state.difficulty + (3 - grade) * 0.2, 1.0, 10.0)

    reps, lapses = state.repetitions, state.lapses
    if grade == GRADE_AGAIN:
        new_s = DEFAULT_STABILITY      # lapse: reset stability
        lapses += 1
        reps = 0
    else:
        factor = {GRADE_HARD: 1.3, GRADE_GOOD: 2.5, GRADE_EASY: 3.5}[grade]
        # Easier concepts (lower difficulty) gain a bit more stability.
        difficulty_bonus = 1.0 + (10.0 - new_d) * 0.02
        new_s = max(1.0, state.stability * factor * difficulty_bonus)
        reps += 1

    new_state = FsrsState(
        stability=round(new_s, 4),
        difficulty=round(new_d, 4),
        retrievability=1.0,   # just reviewed
        repetitions=reps,
        lapses=lapses,
    )
    return new_state, interval_days(new_s)
