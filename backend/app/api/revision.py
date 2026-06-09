from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user_id
from app.repositories.graph_repo import GraphRepository
from app.repositories.assessment_repo import AssessmentRepository
from app.repositories.fsrs_repo import FsrsRepository
from app.services.revision_service import RevisionService
from app.schemas.revision import DueListDTO, ReviewRequest, ReviewResultDTO

router = APIRouter(prefix="/books", tags=["Revision"])


def get_revision_service(session: AsyncSession = Depends(get_db)) -> RevisionService:
    return RevisionService(
        GraphRepository(session), AssessmentRepository(session), FsrsRepository(session)
    )


@router.get("/{book_id}/revision", response_model=DueListDTO)
async def get_due_reviews(
    book_id: str,
    user_id: str = Depends(get_current_user_id),
    service: RevisionService = Depends(get_revision_service),
    session: AsyncSession = Depends(get_db),
):
    result = await service.get_due(user_id, book_id)
    await session.commit()  # mark_due_states may write
    return result


@router.post("/{book_id}/concepts/{concept_id}/review", response_model=ReviewResultDTO)
async def submit_review(
    book_id: str,
    concept_id: str,
    data: ReviewRequest,
    user_id: str = Depends(get_current_user_id),
    service: RevisionService = Depends(get_revision_service),
    session: AsyncSession = Depends(get_db),
):
    result = await service.review(user_id, book_id, concept_id, data.grade)
    await session.commit()
    return result
