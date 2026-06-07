import uuid
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, Numeric, func
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from app.models.base import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    assessment_type = Column(
        ENUM('INITIAL', 'PLACEMENT', 'CHAPTER', 'REVISION', name='assessment_type', create_type=False),
        nullable=False,
    )
    status = Column(
        ENUM('DRAFT', 'IN_PROGRESS', 'COMPLETED', 'ABANDONED', name='assessment_status', create_type=False),
        nullable=False, default='DRAFT',
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_questions = Column(Integer, nullable=True)
    score_percentage = Column(Numeric(5, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AssessmentResponse(Base):
    __tablename__ = "assessment_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("generated_questions.id", ondelete="CASCADE"), nullable=False)
    confidence_level = Column(Integer, nullable=True)
    response = Column(JSONB, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    response_time_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AssessmentOutcome(Base):
    __tablename__ = "assessment_outcomes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    mastery_estimate = Column(Numeric(5, 4), nullable=False)
    placement_state = Column(
        ENUM('MASTERED', 'READY', 'LEARNING', 'WEAK', 'UNKNOWN', name='placement_state', create_type=False),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
