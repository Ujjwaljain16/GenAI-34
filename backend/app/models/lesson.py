from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint, Index, CheckConstraint, ForeignKeyConstraint
import uuid
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, String, func
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from app.models.base import Base


class LessonSession(Base):
    __tablename__ = "lesson_sessions"
    __table_args__ = (
    
            CheckConstraint('completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at', name='chk_lesson_time'),
    
            ForeignKeyConstraint(['concept_id'], ['concepts.id'], ondelete='CASCADE', name='lesson_sessions_concept_id_fkey'),
    
            ForeignKeyConstraint(['curriculum_plan_id'], ['curriculum_plans.id'], ondelete='SET NULL', name='lesson_sessions_curriculum_plan_id_fkey'),
    
            ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='lesson_sessions_user_id_fkey'),
    
            PrimaryKeyConstraint('id', name='lesson_sessions_pkey'),
    
            Index('idx_active_lesson_sessions', 'user_id', postgresql_where="(status = 'IN_PROGRESS'::lesson_status)"),
    
            Index('idx_lesson_sessions_concept', 'concept_id'),
    
            Index('idx_lesson_sessions_content', 'generated_content', postgresql_using='gin'),
    
            Index('idx_lesson_sessions_status', 'status'),
    
            Index('idx_lesson_sessions_user', 'user_id'),
    
            {'comment': 'One session = Socratic teaching of one concept.'}
    
        )


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    curriculum_plan_id = Column(UUID(as_uuid=True), ForeignKey("curriculum_plans.id", ondelete="SET NULL"), nullable=True)
    status = Column(
        ENUM('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'ABANDONED', name='lesson_status', create_type=False),
        nullable=False, default='NOT_STARTED',
    )
    generated_content = Column(JSONB, nullable=False)
    generation_metadata = Column(JSONB, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TutorInteraction(Base):
    __tablename__ = "tutor_interactions"
    __table_args__ = (
    
            CheckConstraint('hint_level >= 0 AND hint_level <= 4', name='chk_hint_level'),
    
            CheckConstraint('latency_ms IS NULL OR latency_ms >= 0', name='chk_latency'),
    
            CheckConstraint('token_input_count IS NULL OR token_input_count >= 0', name='chk_input_tokens'),
    
            CheckConstraint('token_output_count IS NULL OR token_output_count >= 0', name='chk_output_tokens'),
    
            CheckConstraint('turn_index >= 0', name='chk_turn_index'),
    
            ForeignKeyConstraint(['lesson_session_id'], ['lesson_sessions.id'], ondelete='CASCADE', name='tutor_interactions_lesson_session_id_fkey'),
    
            ForeignKeyConstraint(['question_id'], ['generated_questions.id'], ondelete='SET NULL', name='tutor_interactions_question_id_fkey'),
    
            PrimaryKeyConstraint('id', name='tutor_interactions_pkey'),
    
            UniqueConstraint('lesson_session_id', 'turn_index', name='uq_session_turn'),
    
            Index('idx_tutor_interactions_created', 'created_at'),
    
            Index('idx_tutor_interactions_question', 'question_id', postgresql_where='(question_id IS NOT NULL)'),
    
            Index('idx_tutor_interactions_session', 'lesson_session_id'),
    
            {'comment': 'Immutable turn-by-turn Socratic conversation log with turn_index '
    
                    'ordering.'}
    
        )


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_session_id = Column(UUID(as_uuid=True), ForeignKey("lesson_sessions.id", ondelete="CASCADE"), nullable=False)
    turn_index = Column(Integer, nullable=False)
    user_message = Column(Text, nullable=False)
    assistant_message = Column(Text, nullable=False)
    hint_level = Column(Integer, nullable=False, default=0)
    question_id = Column(UUID(as_uuid=True), ForeignKey("generated_questions.id", ondelete="SET NULL"), nullable=True)
    model_name = Column(String(100), nullable=True)
    token_input_count = Column(Integer, nullable=True)
    token_output_count = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
