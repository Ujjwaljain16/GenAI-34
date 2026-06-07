from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fsrs import ConceptFsrs, FsrsReview, MasteryEvent
from app.services.fsrs import FsrsState


class FsrsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_state(self, user_id: str, concept_id: str) -> Optional[ConceptFsrs]:
        r = await self.session.execute(
            select(ConceptFsrs).where(
                ConceptFsrs.user_id == user_id, ConceptFsrs.concept_id == concept_id))
        return r.scalars().first()

    async def upsert_state(self, user_id: str, concept_id: str, state: FsrsState,
                           interval_days: int) -> None:
        now = datetime.now(timezone.utc)
        next_due = now + timedelta(days=interval_days)
        stmt = pg_insert(ConceptFsrs.__table__).values(
            user_id=user_id, concept_id=concept_id,
            stability=state.stability, difficulty=state.difficulty,
            retrievability=state.retrievability, repetitions=state.repetitions,
            lapses=state.lapses, next_due=next_due, last_reviewed_at=now,
        ).on_conflict_do_update(
            constraint="uq_user_concept_fsrs",
            set_={
                "stability": state.stability, "difficulty": state.difficulty,
                "retrievability": state.retrievability, "repetitions": state.repetitions,
                "lapses": state.lapses, "next_due": next_due, "last_reviewed_at": now,
            },
        )
        await self.session.execute(stmt)

    async def log_review(self, user_id: str, concept_id: str, grade: int,
                         before: FsrsState, after: FsrsState, source: str = "REVISION") -> None:
        self.session.add(FsrsReview(
            user_id=user_id, concept_id=concept_id, review_source=source, review_grade=grade,
            stability_before=before.stability, stability_after=after.stability,
            difficulty_before=before.difficulty, difficulty_after=after.difficulty,
            retrievability_before=before.retrievability, retrievability_after=after.retrievability,
        ))

    async def log_mastery_event(self, user_id: str, concept_id: str, source: str,
                                previous: float, new: float, reason: str) -> None:
        self.session.add(MasteryEvent(
            user_id=user_id, concept_id=concept_id, source=source,
            previous_mastery=previous, new_mastery=new, reason=reason))

    async def due_concepts(self, user_id: str, book_id: str) -> List[dict]:
        """Concepts whose next_due has passed, most overdue first."""
        rows = await self.session.execute(
            text("""
                SELECT cf.concept_id, c.name, cf.next_due, cf.stability, cf.retrievability
                FROM concept_fsrs cf
                JOIN concepts c ON c.id = cf.concept_id
                WHERE cf.user_id = :uid AND c.book_id = :bid
                  AND cf.next_due IS NOT NULL AND cf.next_due <= NOW()
                ORDER BY cf.next_due ASC
            """),
            {"uid": user_id, "bid": book_id})
        return [
            {"concept_id": str(r.concept_id), "title": r.name,
             "next_due": r.next_due.isoformat() if r.next_due else None,
             "stability": r.stability, "retrievability": r.retrievability}
            for r in rows
        ]

    async def mark_due_states(self, user_id: str, book_id: str) -> int:
        """Flip MASTERED -> DUE for concepts whose next_due has passed. Returns count."""
        r = await self.session.execute(
            text("""
                UPDATE user_concept_state ucs
                SET state = 'DUE', state_updated_at = NOW()
                FROM concept_fsrs cf, concepts c
                WHERE ucs.user_id = :uid AND ucs.concept_id = cf.concept_id
                  AND cf.user_id = ucs.user_id AND c.id = ucs.concept_id
                  AND c.book_id = :bid
                  AND ucs.state = 'MASTERED'
                  AND cf.next_due IS NOT NULL AND cf.next_due <= NOW()
                RETURNING ucs.id
            """),
            {"uid": user_id, "bid": book_id})
        return len(r.fetchall())
