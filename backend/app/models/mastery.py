import uuid
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, func
from sqlalchemy.dialects.postgresql import UUID, ENUM
from app.models.base import Base


class UserConceptState(Base):
    __tablename__ = "user_concept_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    graph_version = Column(Integer, nullable=False)
    state = Column(
        ENUM('LOCKED', 'AVAILABLE', 'IN_PROGRESS', 'MASTERED', 'DUE', name='node_state', create_type=False),
        nullable=False, default='LOCKED',
    )
    state_updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ConceptMastery(Base):
    __tablename__ = "concept_mastery"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    mastery_score = Column(Numeric(5, 4), nullable=False, default=0)
    mastery_state = Column(
        ENUM('UNKNOWN', 'LEARNING', 'PRACTICING', 'MASTERED', 'FORGOTTEN', name='mastery_state', create_type=False),
        nullable=False, default='UNKNOWN',
    )
    first_mastered_at = Column(DateTime(timezone=True), nullable=True)
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    updated_by_source = Column(
        ENUM('ASSESSMENT', 'LESSON', 'QUIZ', 'REVISION', 'MANUAL', name='review_source', create_type=False),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
