"""
Progress engine — one of the two allowed writers of the learner model
(AGENT.md: Assessment Engine + Progress Engine only).

PR4 scope: record concept completion from a finished lesson (mastery -> MASTERED,
node state -> MASTERED) and re-evaluate the DAG to unlock newly-available
dependents (System Design F#26). PR5 extends this with FSRS scheduling and
review-grade updates.
"""
from __future__ import annotations

from collections import defaultdict
from typing import List

from sqlalchemy import text

from app.repositories.graph_repo import GraphRepository
from app.repositories.assessment_repo import AssessmentRepository
from app.repositories.fsrs_repo import FsrsRepository
from app.services import fsrs as fsrs_engine
from app.services import mastery_engine

MASTERY_ON_LESSON_COMPLETE = 0.9
MASTERED_THRESHOLD = 0.85


class ProgressService:
    def __init__(self, graph_repo: GraphRepository, assess_repo: AssessmentRepository,
                 fsrs_repo: FsrsRepository | None = None):
        self.graph = graph_repo
        self.repo = assess_repo
        self.fsrs = fsrs_repo or FsrsRepository(graph_repo.session)

    async def complete_concept(self, user_id: str, book_id: str, concept_id: str,
                               source: str = "LESSON") -> List[str]:
        """Mark a concept mastered and unlock dependents whose prerequisites are
        now all mastered. Returns the titles of newly-unlocked concepts."""
        gv = await self.graph.active_graph_version(book_id)
        if gv is None:
            return []

        # Write mastery + node state for the completed concept.
        await self.repo.upsert_concept_mastery(user_id, concept_id, MASTERY_ON_LESSON_COMPLETE, "MASTERED", source=source)
        await self.repo.upsert_node_state(user_id, concept_id, gv, "MASTERED")

        # Recompute the mastered set and unlock dependents.
        concepts = await self.graph.concepts(book_id, gv)
        edges = await self.graph.prerequisite_edges(book_id, gv)
        states = await self.graph.node_states(user_id, book_id)
        masteries = {cid: score for cid, (score, _lr) in (await self.graph.masteries(user_id, book_id)).items()}

        direct_prereqs = defaultdict(list)
        for e in edges:
            direct_prereqs[str(e.to_concept_id)].append(str(e.from_concept_id))

        mastered = {str(c.id) for c in concepts
                    if states.get(str(c.id)) == "MASTERED"
                    or masteries.get(str(c.id), 0.0) >= MASTERED_THRESHOLD}
        mastered.add(concept_id)

        unlocked: List[str] = []
        for c in concepts:
            cid = str(c.id)
            cur = states.get(cid)
            if cur in (None, "LOCKED"):
                prereqs = direct_prereqs.get(cid, [])
                if all(p in mastered for p in prereqs):  # roots (no prereqs) included
                    await self.repo.upsert_node_state(user_id, cid, gv, "AVAILABLE")
                    if cur == "LOCKED":
                        unlocked.append(c.name)

        # Enter the spaced-repetition cycle: first successful review schedules
        # the concept for future revision (only if not already tracked).
        if await self.fsrs.get_state(user_id, concept_id) is None:
            state, interval = fsrs_engine.review(fsrs_engine.init_state(), fsrs_engine.GRADE_GOOD)
            await self.fsrs.upsert_state(user_id, concept_id, state, interval)
        return unlocked

    async def record_review(self, user_id: str, book_id: str, concept_id: str, grade: int) -> dict:
        """Grade a spaced-repetition review: update FSRS schedule + mastery, and
        flip the node back to MASTERED on success (System Design G#31)."""
        gv = await self.graph.active_graph_version(book_id)
        before_row = await self.fsrs.get_state(user_id, concept_id)
        before = fsrs_engine.FsrsState(
            stability=before_row.stability, difficulty=before_row.difficulty,
            retrievability=before_row.retrievability,
            repetitions=before_row.repetitions, lapses=before_row.lapses,
        ) if before_row else fsrs_engine.init_state()

        after, interval = fsrs_engine.review(before, grade)
        await self.fsrs.upsert_state(user_id, concept_id, after, interval)
        await self.fsrs.log_review(user_id, concept_id, grade, before, after, source="REVISION")

        # Mastery update via the canonical mastery engine.
        prev_m = await self._current_mastery(user_id, concept_id)
        event = "correct" if grade >= fsrs_engine.GRADE_GOOD else "wrong"
        result = mastery_engine.update_mastery(prev_m, prev_m, event)
        new_state = "MASTERED" if result.mastery >= mastery_engine.MASTERY_THRESHOLD else "PRACTICING"
        await self.repo.upsert_concept_mastery(user_id, concept_id, result.mastery, new_state, source="REVISION")
        await self.fsrs.log_mastery_event(user_id, concept_id, "REVISION", prev_m, result.mastery,
                                          f"revision grade {grade}")

        # Node state: recalled -> back to MASTERED; failed -> stays DUE for retry.
        if gv is not None:
            await self.repo.upsert_node_state(
                user_id, concept_id, gv, "MASTERED" if grade >= fsrs_engine.GRADE_GOOD else "DUE")

        return {
            "concept_id": concept_id, "grade": grade,
            "mastery": round(result.mastery, 4), "interval_days": interval,
            "stability": after.stability, "difficulty": after.difficulty,
        }

    async def _current_mastery(self, user_id: str, concept_id: str) -> float:
        row = await self.fsrs.session.execute(
            text("SELECT mastery_score FROM concept_mastery WHERE user_id = :u AND concept_id = :c"),
            {"u": user_id, "c": concept_id})
        r = row.first()
        return float(r[0]) if r else 0.0
