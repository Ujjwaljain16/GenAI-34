from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint, Index, CheckConstraint, ForeignKeyConstraint
import uuid
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, String, func
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from app.models.base import Base


class GeneratedQuestion(Base):
    __tablename__ = "generated_questions"
    __table_args__ = (
    
            CheckConstraint('difficulty_level >= 1 AND difficulty_level <= 5', name='chk_question_difficulty'),
    
            ForeignKeyConstraint(['concept_id'], ['concepts.id'], ondelete='CASCADE', name='generated_questions_concept_id_fkey'),
    
            PrimaryKeyConstraint('id', name='generated_questions_pkey'),
    
            Index('idx_generated_questions_answer_key', 'answer_key', postgresql_using='gin'),
    
            Index('idx_generated_questions_concept', 'concept_id'),
    
            Index('idx_generated_questions_concept_source', 'concept_id', 'question_source'),
    
            Index('idx_generated_questions_difficulty', 'difficulty_level'),
    
            Index('idx_generated_questions_source', 'question_source'),
    
            Index('idx_generated_questions_type', 'question_type'),
    
            {'comment': 'Questions per concept. source=USER_ASKED|ASSESSMENT_MISS powers '
    
                    'targeted revision.'}
    
        )


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    question_type = Column(
        ENUM('MCQ', 'TRUE_FALSE', 'SHORT_ANSWER', 'SCENARIO', 'ORDERING', 'MATCHING',
             name='question_type', create_type=False),
        nullable=False,
    )
    question_source = Column(
        ENUM('GENERATED', 'USER_ASKED', 'ASSESSMENT_MISS', 'REVISION',
             name='question_source', create_type=False),
        nullable=False, default='GENERATED',
    )
    difficulty_level = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    # JSONB: { options: [...], correct_option: int, expected_answer: str, hints: [...], bloom_level: str }
    answer_key = Column(JSONB, nullable=False)
    explanation = Column(Text, nullable=True)
    generation_model = Column(String(100), nullable=True)
    generation_version = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
