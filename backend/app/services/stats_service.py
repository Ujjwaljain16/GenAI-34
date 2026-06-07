"""
Dashboard / stats / streaks / notifications (System Design Section H).

Read-only aggregation over the learner model. Streaks are derived from existing
activity timestamps (reviews, lesson + assessment completions) so no extra
write path is needed.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import List

from app.repositories.stats_repo import StatsRepository
from app.schemas.dashboard import (
    BookProgressDTO, WeakSpotDTO, DashboardDTO, NotificationDTO,
)


def _round_pct(num: int, den: int) -> float:
    return round(100.0 * num / den, 1) if den else 0.0


def current_streak(dates: List[date], today: date | None = None) -> int:
    """Consecutive-day streak ending today or yesterday (grace for not-yet-today)."""
    if not dates:
        return 0
    today = today or date.today()
    s = set(dates)
    start = today if today in s else (today - timedelta(days=1))
    if start not in s:
        return 0
    streak, cursor = 0, start
    while cursor in s:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


class StatsService:
    def __init__(self, repo: StatsRepository):
        self.repo = repo

    async def dashboard(self, user_id: str) -> DashboardDTO:
        books_raw = await self.repo.per_book_progress(user_id)
        totals = await self.repo.global_totals(user_id)
        weak = await self.repo.weak_spots(user_id)
        dates = await self.repo.activity_dates(user_id)
        total_due = await self.repo.total_due(user_id)

        books = [
            BookProgressDTO(
                bookId=str(b["id"]), title=b["title"], author=b.get("author"),
                status=str(b["status"]).lower(),
                totalConcepts=b["total"], masteredConcepts=b["mastered"],
                percentMastered=_round_pct(b["mastered"], b["total"]),
                percentRevealed=_round_pct(b["revealed"], b["total"]),
                dueToday=b["due"],
            )
            for b in books_raw
        ]
        streak = current_streak(dates)
        return DashboardDTO(
            conceptsMastered=totals["mastered"], conceptsTracked=totals["tracked"],
            avgMastery=round(totals["avg_mastery"], 3), totalDue=total_due,
            globalStreak=streak, studiedToday=(date.today() in set(dates)),
            books=books,
            weakSpots=[WeakSpotDTO(title=w["title"], bookTitle=w["book_title"],
                                   mastery=float(w["mastery_score"])) for w in weak],
        )

    async def notifications(self, user_id: str) -> List[NotificationDTO]:
        """Derive live notifications from current state (replaces the [] stub)."""
        out: List[NotificationDTO] = []
        books = await self.repo.per_book_progress(user_id)
        for b in books:
            bid = str(b["id"])
            status = str(b["status"]).upper()
            if b["due"] > 0:
                out.append(NotificationDTO(
                    id=f"due-{bid}", type="due_reviews",
                    message=f"You have {b['due']} review(s) due in '{b['title']}'.",
                    link=f"/book/{bid}/revision"))
            if status in ("KG_BUILT", "KG_VERIFIED"):
                out.append(NotificationDTO(
                    id=f"review-{bid}", type="needs_review",
                    message=f"'{b['title']}' graph is ready to review.",
                    link=f"/book/{bid}"))
            elif status == "READY" and b["total"] > 0 and b["mastered"] == 0 and b["revealed"] == 0:
                out.append(NotificationDTO(
                    id=f"assess-{bid}", type="take_assessment",
                    message=f"'{b['title']}' is ready — take the placement assessment.",
                    link=f"/book/{bid}/assessment"))

        dates = await self.repo.activity_dates(user_id)
        streak = current_streak(dates)
        if streak > 0 and date.today() not in set(dates):
            out.append(NotificationDTO(
                id="streak", type="streak",
                message=f"Keep your {streak}-day streak alive — study today!", link="/"))
        return out
