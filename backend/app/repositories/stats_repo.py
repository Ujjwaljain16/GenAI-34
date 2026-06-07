from datetime import date
from typing import List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class StatsRepository:
    """Read-only aggregation for the dashboard / stats / notifications."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def per_book_progress(self, user_id: str) -> List[dict]:
        rows = await self.session.execute(
            text("""
                SELECT b.id, b.title, b.author, b.status::text AS status,
                       COUNT(c.id) AS total,
                       COUNT(*) FILTER (WHERE ucs.state = 'MASTERED') AS mastered,
                       COUNT(*) FILTER (WHERE ucs.state IS NOT NULL AND ucs.state <> 'LOCKED') AS revealed,
                       COUNT(*) FILTER (WHERE ucs.state = 'DUE') AS due
                FROM books b
                JOIN user_books ub ON ub.book_id = b.id AND ub.user_id = :uid
                LEFT JOIN concepts c
                    ON c.book_id = b.id
                   AND c.graph_version = (SELECT MAX(graph_version) FROM concepts WHERE book_id = b.id)
                LEFT JOIN user_concept_state ucs
                    ON ucs.concept_id = c.id AND ucs.user_id = :uid
                GROUP BY b.id, b.title, b.author, b.status
                ORDER BY b.created_at DESC
            """),
            {"uid": user_id})
        return [dict(r._mapping) for r in rows]

    async def global_totals(self, user_id: str) -> dict:
        r = await self.session.execute(
            text("""
                SELECT
                  COUNT(*) FILTER (WHERE mastery_state = 'MASTERED') AS mastered,
                  COUNT(*) AS tracked,
                  COALESCE(AVG(mastery_score), 0) AS avg_mastery
                FROM concept_mastery WHERE user_id = :uid
            """),
            {"uid": user_id})
        row = r.first()
        return {"mastered": row.mastered or 0, "tracked": row.tracked or 0,
                "avg_mastery": float(row.avg_mastery or 0.0)}

    async def weak_spots(self, user_id: str, limit: int = 10) -> List[dict]:
        rows = await self.session.execute(
            text("""
                SELECT c.name AS title, b.title AS book_title, cm.mastery_score
                FROM concept_mastery cm
                JOIN concepts c ON c.id = cm.concept_id
                JOIN books b ON b.id = c.book_id
                WHERE cm.user_id = :uid AND cm.mastery_score < 0.45
                ORDER BY cm.mastery_score ASC
                LIMIT :lim
            """),
            {"uid": user_id, "lim": limit})
        return [dict(r._mapping) for r in rows]

    async def activity_dates(self, user_id: str) -> List[date]:
        """Distinct UTC dates with any learning activity, newest first."""
        rows = await self.session.execute(
            text("""
                SELECT DISTINCT d FROM (
                    SELECT date(reviewed_at) AS d FROM fsrs_reviews WHERE user_id = :uid
                    UNION
                    SELECT date(completed_at) FROM lesson_sessions WHERE user_id = :uid AND completed_at IS NOT NULL
                    UNION
                    SELECT date(completed_at) FROM assessments WHERE user_id = :uid AND completed_at IS NOT NULL
                ) t
                WHERE d IS NOT NULL
                ORDER BY d DESC
            """),
            {"uid": user_id})
        return [r[0] for r in rows]

    async def total_due(self, user_id: str) -> int:
        r = await self.session.execute(
            text("SELECT COUNT(*) FROM concept_fsrs WHERE user_id = :uid AND next_due IS NOT NULL AND next_due <= NOW()"),
            {"uid": user_id})
        return int(r.scalar() or 0)
