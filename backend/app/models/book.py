import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id")) # We'll assume the FK is to users.id
    title = Column(Text, nullable=False)
    author = Column(Text)
    description = Column(Text)
    status = Column(ENUM('UPLOADING', 'PARSING', 'EXTRACTING_CONCEPTS', 'KG_BUILT', 'KG_VERIFIED', 'READY', name='book_status', create_type=False), nullable=False, default='UPLOADING')
    visibility = Column(ENUM('PRIVATE', 'PUBLIC', name='book_visibility', create_type=False), nullable=False, default='PRIVATE')
    source_type = Column(String(50), nullable=False)
    file_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    build_jobs = relationship("GraphBuildJob", back_populates="book", cascade="all, delete-orphan")
    graph_versions = relationship("GraphVersion", back_populates="book", cascade="all, delete-orphan")

class GraphBuildJob(Base):
    __tablename__ = "graph_build_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    graph_version = Column(Integer, nullable=False)
    status = Column(ENUM('QUEUED', 'PARSING', 'CHUNKING', 'EXTRACTING_CONCEPTS', 'CANONICALIZING', 'EXTRACTING_RELATIONSHIPS', 'VALIDATING', 'REPAIRING', 'PUBLISHING', 'COMPLETED', 'FAILED', name='graph_build_status', create_type=False), nullable=False, default='QUEUED')
    current_stage = Column(String(50), nullable=True)
    current_offset = Column(Integer, default=0, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    nodes_created = Column(Integer)
    edges_created = Column(Integer)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    book = relationship("Book", back_populates="build_jobs")
    versions_produced = relationship("GraphVersion", back_populates="build_job")

class GraphVersion(Base):
    __tablename__ = "graph_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    build_job_id = Column(UUID(as_uuid=True), ForeignKey("graph_build_jobs.id", ondelete="RESTRICT"), nullable=False)
    node_count = Column(Integer, nullable=False, default=0)
    edge_count = Column(Integer, nullable=False, default=0)
    label = Column(Text, nullable=True)
    is_current = Column(String, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    book = relationship("Book", back_populates="graph_versions")
    build_job = relationship("GraphBuildJob", back_populates="versions_produced")

class UserBook(Base):
    __tablename__ = "user_books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    pinned_graph_version_id = Column(UUID(as_uuid=True), ForeignKey("graph_versions.id", ondelete="RESTRICT"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    estimated_minutes = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class BookUpload(Base):
    __tablename__ = "book_uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    original_filename = Column(Text, nullable=False)
    storage_path = Column(Text, nullable=False)
    file_size_bytes = Column(Integer)
    mime_type = Column(Text)
    upload_status = Column(ENUM('PENDING', 'STORED', 'FAILED', name='upload_status', create_type=False), nullable=False, default='PENDING')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class GraphValidationResult(Base):
    __tablename__ = "graph_validation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    graph_version_id = Column(UUID(as_uuid=True), ForeignKey("graph_versions.id", ondelete="CASCADE"))
    rule_code = Column(Text, nullable=False)
    passed = Column(Boolean, nullable=False)
    severity = Column(Text, nullable=False)
    detail = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class GraphRepairLog(Base):
    __tablename__ = "graph_repair_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    graph_version_id = Column(UUID(as_uuid=True), ForeignKey("graph_versions.id", ondelete="CASCADE"))
    operation = Column(Text, nullable=False)
    artifact_id = Column(UUID(as_uuid=True))
    reason = Column(Text, nullable=False)
    before_value = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class GraphVersionEvent(Base):
    __tablename__ = "graph_version_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    graph_version_id = Column(UUID(as_uuid=True), ForeignKey("graph_versions.id", ondelete="CASCADE"))
    event_type = Column(Text, nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    notes = Column(Text)
    metadata_ = Column("metadata", JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class GraphAuditEvent(Base):
    __tablename__ = "graph_audit_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    graph_version_id = Column(UUID(as_uuid=True), ForeignKey("graph_versions.id", ondelete="CASCADE"))
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(Text, nullable=False)
    entity_type = Column(Text, nullable=False)
    entity_id = Column(UUID(as_uuid=True))
    before_value = Column(JSONB)
    after_value = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
