from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user_id
from app.repositories.assessment_repo import AssessmentRepository
from app.services.assessment_service import AssessmentService
from app.schemas.assessment import (
    StartAssessmentRequest,
    StartAssessmentResponse,
    SubmitResponseRequest,
    SubmitResponseResponse,
    AssessmentResultDTO,
)

router = APIRouter(prefix="/assessments", tags=["Assessment"])


def get_assessment_service(
    session: AsyncSession = Depends(get_db),
) -> AssessmentService:
    return AssessmentService(AssessmentRepository(session))


@router.post("", response_model=StartAssessmentResponse, status_code=201)
async def start_assessment(
    data: StartAssessmentRequest,
    user_id: str = Depends(get_current_user_id),
    service: AssessmentService = Depends(get_assessment_service),
    session: AsyncSession = Depends(get_db),
):
    result = await service.start_assessment(user_id, data.book_id)
    await session.commit()
    return result


@router.post("/{assessment_id}/responses", response_model=SubmitResponseResponse)
async def submit_response(
    assessment_id: str,
    data: SubmitResponseRequest,
    user_id: str = Depends(get_current_user_id),
    service: AssessmentService = Depends(get_assessment_service),
    session: AsyncSession = Depends(get_db),
):
    result = await service.submit_response(user_id, assessment_id, data)
    await session.commit()
    return result


@router.post("/{assessment_id}/complete", response_model=AssessmentResultDTO)
async def complete_assessment(
    assessment_id: str,
    user_id: str = Depends(get_current_user_id),
    service: AssessmentService = Depends(get_assessment_service),
    session: AsyncSession = Depends(get_db),
):
    # Atomic: scoring + mastery seed + node-state seed + DNA all commit together,
    # or roll back as one unit if any step raises.
    result = await service.complete_assessment(user_id, assessment_id)
    await session.commit()
    return result


@router.get("/{assessment_id}/results", response_model=AssessmentResultDTO)
async def get_results(
    assessment_id: str,
    user_id: str = Depends(get_current_user_id),
    service: AssessmentService = Depends(get_assessment_service),
):
    return await service.get_results(user_id, assessment_id)
