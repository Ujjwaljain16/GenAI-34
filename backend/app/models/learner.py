import uuid
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, String, func
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from app.models.base import Base


class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    confidence_level = Column(Integer, nullable=True)
    experience_level = Column(
        ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED', name='experience_level', create_type=False),
        nullable=True,
    )
    preferred_examples = Column(String(100), nullable=True)
    learning_velocity = Column(String(20), nullable=True)
    preferred_study_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class LearningDNA(Base):
    __tablename__ = "learning_dna"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    dna_version = Column(Integer, nullable=False)
    dna_data = Column(JSONB, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
