"""
Revision engine (System Design Section G) — the daily review heartbeat.

Surfaces FSRS-due concepts and feeds review grades back into the schedule +
mastery via the Progress engine.
"""

from __future__ import annotations

from fastapi import HTTPException

from app.repositories.graph_repo import GraphRepository
from app.repositories.assessment_repo import AssessmentRepository
from app.repositories.fsrs_repo import FsrsRepository
from app.services.progress_service import ProgressService
from app.schemas.revision import DueItemDTO, DueListDTO, ReviewResultDTO


class RevisionService:
    def __init__(
        self,
        graph_repo: GraphRepository,
        assess_repo: AssessmentRepository,
        fsrs_repo: FsrsRepository,
    ):
        self.graph = graph_repo
        self.assess = assess_repo
        self.fsrs = fsrs_repo

    async def get_due(self, user_id: str, book_id: str) -> DueListDTO:
        if not await self.graph.is_enrolled(user_id, book_id):
            raise HTTPException(
                status_code=404, detail="Book not found in your library."
            )
        # Reflect newly-due concepts in the node states (MASTERED -> DUE).
        await self.fsrs.mark_due_states(user_id, book_id)
        due = await self.fsrs.due_concepts(user_id, book_id)
        return DueListDTO(
            bookId=book_id,
            count=len(due),
            due=[
                DueItemDTO(
                    conceptId=d["concept_id"],
                    title=d["title"],
                    nextDue=d["next_due"],
                    retrievability=d["retrievability"],
                )
                for d in due
            ],
        )

    async def review(
        self, user_id: str, book_id: str, concept_id: str, grade: int
    ) -> ReviewResultDTO:
        if not await self.graph.is_enrolled(user_id, book_id):
            raise HTTPException(
                status_code=404, detail="Book not found in your library."
            )
        progress = ProgressService(self.graph, self.assess, self.fsrs)
        r = await progress.record_review(user_id, book_id, concept_id, grade)
        return ReviewResultDTO(
            conceptId=concept_id,
            grade=grade,
            mastery=r["mastery"],
            intervalDays=r["interval_days"],
            stability=r["stability"],
            difficulty=r["difficulty"],
        )
