from sqlalchemy import (
    PrimaryKeyConstraint,
    UniqueConstraint,
    Index,
    CheckConstraint,
    ForeignKeyConstraint,
)
import uuid
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base


class DailyPlan(Base):
    __tablename__ = "daily_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    book_id = Column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    plan_date = Column(Date, nullable=False)
    learn_concept_ids = Column(JSONB, nullable=False, default=list)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class CurriculumPlan(Base):
    __tablename__ = "curriculum_plans"
    __table_args__ = (
        CheckConstraint("version > 0", name="chk_curriculum_version"),
        ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            ondelete="CASCADE",
            name="curriculum_plans_book_id_fkey",
        ),
        ForeignKeyConstraint(
            ["generated_from_assessment"],
            ["assessments.id"],
            ondelete="SET NULL",
            name="curriculum_plans_generated_from_assessment_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="curriculum_plans_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="curriculum_plans_pkey"),
        UniqueConstraint(
            "user_id", "book_id", "version", name="uq_curriculum_user_book_version"
        ),
        Index("idx_curriculum_book", "book_id"),
        Index("idx_curriculum_json", "curriculum_json", postgresql_using="gin"),
        Index("idx_curriculum_user", "user_id"),
        Index("idx_curriculum_user_book_version", "user_id", "book_id", "version"),
        {"comment": "Generated learning order for a user on a book."},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    book_id = Column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    version = Column(Integer, nullable=False)
    curriculum_json = Column(JSONB, nullable=False)
    generated_from_assessment = Column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
