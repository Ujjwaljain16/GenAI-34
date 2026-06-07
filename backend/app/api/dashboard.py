from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user_id
from app.repositories.stats_repo import StatsRepository
from app.services.stats_service import StatsService
from app.schemas.dashboard import DashboardDTO

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_stats_service(session: AsyncSession = Depends(get_db)) -> StatsService:
    return StatsService(StatsRepository(session))


@router.get("", response_model=DashboardDTO)
async def get_dashboard(
    user_id: str = Depends(get_current_user_id),
    service: StatsService = Depends(get_stats_service),
):
    return await service.dashboard(user_id)
