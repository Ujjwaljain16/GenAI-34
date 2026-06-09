from sqlalchemy import (
    PrimaryKeyConstraint,
    UniqueConstraint,
    Index,
    CheckConstraint,
    ForeignKeyConstraint,
)
import uuid
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, Numeric, func
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from app.models.base import Base


class Assessment(Base):
    __tablename__ = "assessments"
    __table_args__ = (
        CheckConstraint(
            "completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at",
            name="chk_assessment_time",
        ),
        CheckConstraint(
            "score_percentage IS NULL OR score_percentage >= 0::numeric AND score_percentage <= 100::numeric",
            name="chk_score",
        ),
        CheckConstraint(
            "total_questions IS NULL OR total_questions > 0", name="chk_total_questions"
        ),
        ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            ondelete="CASCADE",
            name="assessments_book_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="assessments_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="assessments_pkey"),
        Index(
            "idx_active_assessments",
            "user_id",
            postgresql_where="(status = 'IN_PROGRESS'::assessment_status)",
        ),
        Index("idx_assessment_user_book", "user_id", "book_id"),
        Index("idx_assessments_book", "book_id"),
        Index("idx_assessments_status", "status"),
        Index("idx_assessments_user", "user_id"),
        {"comment": "Placement/chapter/revision assessments per user per book."},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    book_id = Column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    assessment_type = Column(
        ENUM(
            "INITIAL",
            "PLACEMENT",
            "CHAPTER",
            "REVISION",
            name="assessment_type",
            create_type=False,
        ),
        nullable=False,
    )
    status = Column(
        ENUM(
            "DRAFT",
            "IN_PROGRESS",
            "COMPLETED",
            "ABANDONED",
            name="assessment_status",
            create_type=False,
        ),
        nullable=False,
        default="DRAFT",
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_questions = Column(Integer, nullable=True)
    score_percentage = Column(Numeric(5, 2), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class AssessmentResponse(Base):
    __tablename__ = "assessment_responses"
    __table_args__ = (
        CheckConstraint(
            "confidence_level IS NULL OR confidence_level >= 1 AND confidence_level <= 5",
            name="chk_confidence_response",
        ),
        CheckConstraint(
            "response_time_seconds IS NULL OR response_time_seconds >= 0",
            name="chk_response_time",
        ),
        ForeignKeyConstraint(
            ["assessment_id"],
            ["assessments.id"],
            ondelete="CASCADE",
            name="assessment_responses_assessment_id_fkey",
        ),
        ForeignKeyConstraint(
            ["concept_id"],
            ["concepts.id"],
            ondelete="CASCADE",
            name="assessment_responses_concept_id_fkey",
        ),
        ForeignKeyConstraint(
            ["question_id"],
            ["generated_questions.id"],
            ondelete="CASCADE",
            name="assessment_responses_question_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="assessment_responses_pkey"),
        Index("idx_assessment_responses_assessment", "assessment_id"),
        Index("idx_assessment_responses_concept", "concept_id"),
        Index(
            "idx_assessment_responses_miss",
            "concept_id",
            postgresql_where="(is_correct = false)",
        ),
        Index("idx_assessment_responses_question", "question_id"),
        Index("idx_assessment_responses_response", "response", postgresql_using="gin"),
        {
            "comment": "Per-question responses. confidence_level before reveal = "
            "calibration signal."
        },
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
    )
    concept_id = Column(
        UUID(as_uuid=True),
        ForeignKey("concepts.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("generated_questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    confidence_level = Column(Integer, nullable=True)
    response = Column(JSONB, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    response_time_seconds = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class AssessmentOutcome(Base):
    __tablename__ = "assessment_outcomes"
    __table_args__ = (
        CheckConstraint(
            "mastery_estimate >= 0::numeric AND mastery_estimate <= 1::numeric",
            name="chk_mastery_estimate",
        ),
        ForeignKeyConstraint(
            ["assessment_id"],
            ["assessments.id"],
            ondelete="CASCADE",
            name="assessment_outcomes_assessment_id_fkey",
        ),
        ForeignKeyConstraint(
            ["concept_id"],
            ["concepts.id"],
            ondelete="CASCADE",
            name="assessment_outcomes_concept_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="assessment_outcomes_pkey"),
        UniqueConstraint(
            "assessment_id", "concept_id", name="uq_assessment_concept_outcome"
        ),
        Index("idx_assessment_outcomes_assessment", "assessment_id"),
        Index("idx_assessment_outcomes_concept", "concept_id"),
        {"comment": "Per-concept placement result seeding mastery and node_state."},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
    )
    concept_id = Column(
        UUID(as_uuid=True),
        ForeignKey("concepts.id", ondelete="CASCADE"),
        nullable=False,
    )
    mastery_estimate = Column(Numeric(5, 4), nullable=False)
    placement_state = Column(
        ENUM(
            "MASTERED",
            "READY",
            "LEARNING",
            "WEAK",
            "UNKNOWN",
            name="placement_state",
            create_type=False,
        ),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
