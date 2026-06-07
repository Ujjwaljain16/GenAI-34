import uuid
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID, ENUM
from app.models.base import Base


class ConceptFsrs(Base):
    __tablename__ = "concept_fsrs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    stability = Column(Float, nullable=False, default=0.4)
    difficulty = Column(Float, nullable=False, default=5.0)
    retrievability = Column(Float, nullable=False, default=1.0)
    repetitions = Column(Integer, nullable=False, default=0)
    lapses = Column(Integer, nullable=False, default=0)
    next_due = Column(DateTime(timezone=True), nullable=True)
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class FsrsReview(Base):
    __tablename__ = "fsrs_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    review_source = Column(
        ENUM('ASSESSMENT', 'LESSON', 'QUIZ', 'REVISION', 'MANUAL', name='review_source', create_type=False),
        nullable=False,
    )
    review_grade = Column(Integer, nullable=False)
    stability_before = Column(Float, nullable=True)
    stability_after = Column(Float, nullable=True)
    difficulty_before = Column(Float, nullable=True)
    difficulty_after = Column(Float, nullable=True)
    retrievability_before = Column(Float, nullable=True)
    retrievability_after = Column(Float, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MasteryEvent(Base):
    __tablename__ = "mastery_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    source = Column(
        ENUM('ASSESSMENT', 'LESSON', 'QUIZ', 'REVISION', 'MANUAL', name='review_source', create_type=False),
        nullable=False,
    )
    previous_mastery = Column(Numeric(5, 4), nullable=True)
    new_mastery = Column(Numeric(5, 4), nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
