from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user_id
from app.repositories.stats_repo import StatsRepository
from app.services.stats_service import StatsService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
async def get_notifications(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    # Derived live from learner state (due reviews, books to review/assess, streak).
    service = StatsService(StatsRepository(session))
    notifications = await service.notifications(user_id)
    return {"notifications": [n.model_dump(by_alias=True) for n in notifications]}
