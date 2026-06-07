from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint, Index, CheckConstraint, ForeignKeyConstraint
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
    __table_args__ = (
    
            CheckConstraint('dna_version > 0', name='chk_dna_version'),
    
            ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='learning_dna_user_id_fkey'),
    
            PrimaryKeyConstraint('id', name='learning_dna_pkey'),
    
            UniqueConstraint('user_id', 'dna_version', name='uq_user_dna_version'),
    
            Index('idx_learning_dna_data', 'dna_data', postgresql_using='gin'),
    
            Index('idx_learning_dna_user', 'user_id'),
    
            Index('uq_active_dna_per_user', 'user_id', postgresql_where='(is_active = true)', unique=True),
    
            {'comment': 'Versioned personalized learner model. Append-only.'}
    
        )


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    dna_version = Column(Integer, nullable=False)
    dna_data = Column(JSONB, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
