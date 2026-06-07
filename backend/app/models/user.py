import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, func, Date, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(ENUM('STUDENT', 'TEACHER', 'ADMIN', name='user_role', create_type=False), nullable=False, default='STUDENT')
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    daily_new_node_cap = Column(Integer, nullable=False, default=10)
    daily_reminder_time = Column(String(5), nullable=True)
    session_length_pref = Column(Integer, nullable=False, default=30)
    notify_reminders = Column(Boolean, nullable=False, default=True)
    notify_due_reviews = Column(Boolean, nullable=False, default=True)
    notify_processing = Column(Boolean, nullable=False, default=True)
    global_streak = Column(Integer, nullable=False, default=0)
    last_active_date = Column(Date, nullable=True)

from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy import Numeric, Boolean, Date

class ContentCompletion(Base):
    __tablename__ = "content_completions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content_type = Column(String(50), nullable=False)
    content_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class DailyActivity(Base):
    __tablename__ = "daily_activity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activity_date = Column(Date, nullable=False)
    minutes_studied = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class LearningStreak(Base):
    __tablename__ = "learning_streaks"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    current_streak_days = Column(Integer, nullable=False, default=0)
    longest_streak_days = Column(Integer, nullable=False, default=0)
    last_activity_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class BookStreak(Base):
    __tablename__ = "book_streaks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    current_streak_days = Column(Integer, nullable=False, default=0)
    longest_streak_days = Column(Integer, nullable=False, default=0)
    last_activity_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ProgressSnapshot(Base):
    __tablename__ = "progress_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    snapshot_date = Column(Date, nullable=False)
    concepts_mastered = Column(Integer, nullable=False, default=0)
    concepts_in_progress = Column(Integer, nullable=False, default=0)
    total_minutes_studied = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(ENUM('STREAK_WARNING', 'STREAK_LOST', 'STREAK_MILESTONE', 'MASTERY_MILESTONE', 'SYSTEM', name='notification_type', create_type=False), nullable=False)
    title = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    action_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
