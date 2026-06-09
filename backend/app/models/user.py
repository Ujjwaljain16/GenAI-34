from sqlalchemy import (
    PrimaryKeyConstraint,
    UniqueConstraint,
    Index,
    CheckConstraint,
    ForeignKeyConstraint,
)
import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
    func,
    Date,
    Text,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID, ENUM
from app.models.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="users_pkey"),
        UniqueConstraint("email", name="users_email_key"),
        Index("idx_users_active", "is_active", postgresql_where="(is_active = true)"),
        Index("idx_users_email", "email"),
        Index("idx_users_role", "role"),
        {"comment": "Platform users."},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(
        ENUM("STUDENT", "TEACHER", "ADMIN", name="user_role", create_type=False),
        nullable=False,
        default="STUDENT",
    )
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    avatar_url = Column(String(500), nullable=True)
    daily_new_node_cap = Column(Integer, nullable=False, default=10)
    daily_reminder_time = Column(String(5), nullable=True)
    session_length_pref = Column(Integer, nullable=False, default=30)
    notify_reminders = Column(Boolean, nullable=False, default=True)
    notify_due_reviews = Column(Boolean, nullable=False, default=True)
    notify_processing = Column(Boolean, nullable=False, default=True)
    global_streak = Column(Integer, nullable=False, default=0)
    last_active_date = Column(Date, nullable=True)


class ContentCompletion(Base):
    __tablename__ = "content_completions"
    __table_args__ = (
        CheckConstraint("content_version > 0", name="chk_content_version"),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="content_completions_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="content_completions_pkey"),
        UniqueConstraint(
            "user_id",
            "content_type",
            "content_id",
            "content_version",
            name="uq_completion",
        ),
        Index("idx_content_completions_content", "content_type", "content_id"),
        Index("idx_content_completions_user", "user_id"),
        {"comment": "Idempotency guard for bonus awards. First completion wins."},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content_type = Column(String(50), nullable=False)
    content_id = Column(UUID(as_uuid=True), nullable=False)
    content_version = Column(Integer, nullable=False, default=1)
    completed_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)


class DailyActivity(Base):
    __tablename__ = "daily_activity"
    __table_args__ = (
        CheckConstraint("assessments_completed >= 0", name="chk_assessments_comp"),
        CheckConstraint("concepts_learned >= 0", name="chk_concepts_learned"),
        CheckConstraint("concepts_reviewed >= 0", name="chk_concepts_reviewed"),
        CheckConstraint("lessons_completed >= 0", name="chk_lessons_completed"),
        CheckConstraint("minutes_studied >= 0", name="chk_minutes_studied"),
        CheckConstraint("questions_answered >= 0", name="chk_questions_answered"),
        CheckConstraint("tutor_messages_sent >= 0", name="chk_tutor_messages"),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="daily_activity_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="daily_activity_pkey"),
        UniqueConstraint("user_id", "activity_date", name="uq_daily_activity"),
        Index("idx_daily_activity_date", "activity_date"),
        Index("idx_daily_activity_user", "user_id"),
        Index("idx_daily_activity_user_date", "user_id", "activity_date"),
        {
            "comment": "One row per (user, date). Source of truth for streak computation."
        },
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    activity_date = Column(Date, nullable=False)
    minutes_studied = Column(Integer, nullable=False, default=0)
    tutor_messages_sent = Column(Integer, nullable=False, default=0)
    lessons_completed = Column(Integer, nullable=False, default=0)
    assessments_completed = Column(Integer, nullable=False, default=0)
    concepts_learned = Column(Integer, nullable=False, default=0)
    questions_answered = Column(Integer, nullable=False, default=0)
    concepts_reviewed = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class LearningStreak(Base):
    __tablename__ = "learning_streaks"
    __table_args__ = (
        CheckConstraint("current_streak_days >= 0", name="chk_current_streak"),
        CheckConstraint("longest_streak_days >= 0", name="chk_longest_streak"),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="learning_streaks_user_id_fkey",
        ),
        PrimaryKeyConstraint("user_id", name="learning_streaks_pkey"),
        {"comment": "Global daily-activity streak per user."},
    )

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    current_streak_days = Column(Integer, nullable=False, default=0)
    longest_streak_days = Column(Integer, nullable=False, default=0)
    last_activity_date = Column(Date)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class BookStreak(Base):
    __tablename__ = "book_streaks"
    __table_args__ = (
        CheckConstraint("current_streak_days >= 0", name="chk_book_current_streak"),
        CheckConstraint("longest_streak_days >= 0", name="chk_book_longest_streak"),
        ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            ondelete="CASCADE",
            name="book_streaks_book_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="book_streaks_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="book_streaks_pkey"),
        UniqueConstraint("user_id", "book_id", name="uq_book_streak"),
        Index("idx_book_streaks_book", "book_id"),
        Index("idx_book_streaks_user", "user_id"),
        {"comment": "Per-book consistency streak per user."},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    book_id = Column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    current_streak_days = Column(Integer, nullable=False, default=0)
    longest_streak_days = Column(Integer, nullable=False, default=0)
    last_activity_date = Column(Date)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class ProgressSnapshot(Base):
    __tablename__ = "progress_snapshots"
    __table_args__ = (
        CheckConstraint(
            "average_mastery IS NULL OR average_mastery >= 0::numeric AND average_mastery <= 1::numeric",
            name="chk_avg_mastery",
        ),
        CheckConstraint(
            "average_retrievability IS NULL OR average_retrievability >= 0::numeric AND average_retrievability <= 1::numeric",
            name="chk_avg_retrievability",
        ),
        CheckConstraint(
            "overall_progress >= 0::numeric AND overall_progress <= 100::numeric",
            name="chk_progress",
        ),
        ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            ondelete="CASCADE",
            name="progress_snapshots_book_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="progress_snapshots_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="progress_snapshots_pkey"),
        UniqueConstraint("user_id", "book_id", "snapshot_date", name="uq_snapshot"),
        Index("idx_progress_snapshots_book", "book_id"),
        Index("idx_progress_snapshots_date", "snapshot_date"),
        Index("idx_progress_snapshots_user", "user_id"),
        Index("idx_progress_user_book", "user_id", "book_id"),
        {"comment": "Daily snapshot of per-book progress metrics for trend charts."},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    book_id = Column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    snapshot_date = Column(Date, nullable=False)
    total_concepts = Column(Integer, nullable=False, default=0)
    learning_concepts = Column(Integer, nullable=False, default=0)
    mastered_concepts = Column(Integer, nullable=False, default=0)
    weak_concepts = Column(Integer, nullable=False, default=0)
    average_mastery = Column(Numeric(5, 4))
    average_retrievability = Column(Numeric(5, 4))
    overall_progress = Column(Numeric(5, 2), nullable=False, default=0)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="notifications_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="notifications_pkey"),
        Index(
            "idx_notifications_unread", "user_id", postgresql_where="(is_read = false)"
        ),
        Index("idx_notifications_user", "user_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type = Column(
        ENUM(
            "STREAK_WARNING",
            "STREAK_LOST",
            "STREAK_MILESTONE",
            "MASTERY_MILESTONE",
            "SYSTEM",
            name="notification_type",
            create_type=False,
        ),
        nullable=False,
    )
    title = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    action_url = Column(Text)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
