from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint, Index, CheckConstraint, ForeignKeyConstraint
import uuid
from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, DateTime, func, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base

class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
    
            CheckConstraint('page_count IS NULL OR page_count > 0', name='chk_page_count'),
    
            CheckConstraint('processing_completed_at IS NULL OR processing_started_at IS NULL OR processing_completed_at >= processing_started_at', name='chk_processing_time'),
    
            CheckConstraint("source_type::text = ANY (ARRAY['PDF'::character varying, 'EPUB'::character varying, 'TXT'::character varying, 'DOCX'::character varying, 'URL'::character varying]::text[])", name='books_source_type_check'),
    
            ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='SET NULL', name='fk_books_owner'),
    
            PrimaryKeyConstraint('id', name='books_pkey'),
    
            Index('idx_books_created_at', 'created_at'),
    
            Index('idx_books_owner', 'owner_id'),
    
            Index('idx_books_status', 'status'),
    
            Index('idx_books_title', 'title'),
    
            Index('idx_books_visibility', 'visibility'),
    
            {'comment': 'Uploaded books and learning resources. Status lifecycle: '
    
                    'UPLOADINGΓåÆPARSINGΓåÆEXTRACTING_CONCEPTSΓåÆKG_BUILTΓåÆKG_VERIFIEDΓåÆREADY.'}
    
        )


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id")) # We'll assume the FK is to users.id
    title = Column(Text, nullable=False)
    author = Column(Text)
    description = Column(Text)
    status = Column(ENUM('UPLOADING', 'PARSING', 'EXTRACTING_CONCEPTS', 'KG_BUILT', 'KG_VERIFIED', 'READY', name='book_status', create_type=False), nullable=False, default='UPLOADING')
    visibility = Column(ENUM('PRIVATE', 'PUBLIC', name='book_visibility', create_type=False), nullable=False, default='PRIVATE')
    source_type = Column(String(50), nullable=False)
    file_url = Column(Text, nullable=True)
    language = Column(String(10), server_default="en", nullable=False)
    page_count = Column(Integer)
    file_size_bytes = Column(BigInteger)
    processing_started_at = Column(DateTime(timezone=True))
    processing_completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    build_jobs = relationship("GraphBuildJob", back_populates="book", cascade="all, delete-orphan")
    graph_versions = relationship("GraphVersion", back_populates="book", cascade="all, delete-orphan")

class GraphBuildJob(Base):
    __tablename__ = "graph_build_jobs"
    __table_args__ = (
    
            CheckConstraint('chunks_processed IS NULL OR chunks_processed >= 0', name='chk_chunks_processed'),
    
            CheckConstraint('completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at', name='chk_graph_job_time'),
    
            CheckConstraint('concepts_created IS NULL OR concepts_created >= 0', name='chk_concepts_created'),
    
            CheckConstraint('edges_created IS NULL OR edges_created >= 0', name='chk_edges_created'),
    
            CheckConstraint('graph_version > 0', name='chk_graph_version_positive'),
    
            CheckConstraint('nodes_created IS NULL OR nodes_created >= 0', name='chk_nodes_created'),
    
            ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE', name='graph_build_jobs_book_id_fkey'),
    
            ForeignKeyConstraint(['book_upload_id'], ['book_uploads.id'], ondelete='CASCADE', name='graph_build_jobs_book_upload_id_fkey'),
    
            PrimaryKeyConstraint('id', name='graph_build_jobs_pkey'),
    
            Index('idx_graph_build_jobs_book', 'book_id'),
    
            Index('idx_graph_build_jobs_metadata', 'metadata', postgresql_using='gin'),
    
            Index('idx_graph_build_jobs_status', 'status'),
    
            Index('idx_graph_build_jobs_version', 'book_id', 'graph_version'),
    
            Index('uq_completed_graph_version', 'book_id', 'graph_version', postgresql_where="(status = 'COMPLETED'::graph_build_status)", unique=True),
    
            {'comment': 'Async pipeline job tracker. Only one COMPLETED build per (book, '
    
                    'graph_version).'}
    
        )


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
    book_upload_id = Column(UUID(as_uuid=True), ForeignKey("book_uploads.id", ondelete="CASCADE"))
    concepts_created = Column(Integer)
    chunks_processed = Column(Integer)
    metadata_ = Column("metadata", JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    book = relationship("Book", back_populates="build_jobs")
    versions_produced = relationship("GraphVersion", back_populates="build_job")

class GraphVersion(Base):
    __tablename__ = "graph_versions"
    __table_args__ = (
    
            CheckConstraint('edge_count >= 0', name='chk_gv_edge_count'),
    
            CheckConstraint('node_count >= 0', name='chk_gv_node_count'),
    
            CheckConstraint('version > 0', name='chk_gv_version'),
    
            ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE', name='graph_versions_book_id_fkey'),
    
            ForeignKeyConstraint(['build_job_id'], ['graph_build_jobs.id'], ondelete='RESTRICT', name='graph_versions_build_job_id_fkey'),
    
            PrimaryKeyConstraint('id', name='graph_versions_pkey'),
    
            UniqueConstraint('book_id', 'version', name='uq_graph_version_per_book'),
    
            Index('idx_graph_versions_book', 'book_id'),
    
            Index('idx_graph_versions_current', 'book_id', postgresql_where='(is_current = true)'),
    
            Index('uq_current_graph_version_per_book', 'book_id', postgresql_where='(is_current = true)', unique=True),
    
            {'comment': 'Named snapshot of each completed graph build per book. Single '
    
                    'source for version lookups.'}
    
        )


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    build_job_id = Column(UUID(as_uuid=True), ForeignKey("graph_build_jobs.id", ondelete="RESTRICT"), nullable=False)
    node_count = Column(Integer, nullable=False, default=0)
    edge_count = Column(Integer, nullable=False, default=0)
    label = Column(Text, nullable=True)
    is_current = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    book = relationship("Book", back_populates="graph_versions")
    build_job = relationship("GraphBuildJob", back_populates="versions_produced")

class UserBook(Base):
    __tablename__ = "user_books"
    __table_args__ = (
    
            ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE', name='user_books_book_id_fkey'),
    
            ForeignKeyConstraint(['current_chapter_id'], ['chapters.id'], ondelete='SET NULL', name='user_books_current_chapter_id_fkey'),
    
            ForeignKeyConstraint(['pinned_graph_version_id'], ['graph_versions.id'], ondelete='RESTRICT', name='user_books_pinned_graph_version_id_fkey'),
    
            ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='user_books_user_id_fkey'),
    
            PrimaryKeyConstraint('id', name='user_books_pkey'),
    
            UniqueConstraint('user_id', 'book_id', name='uq_user_book'),
    
            Index('idx_user_books_book', 'book_id'),
    
            Index('idx_user_books_user', 'user_id'),
    
            Index('idx_user_books_version', 'pinned_graph_version_id'),
    
            {'comment': 'User enrollment in a book. Pins graph version at enrollment time.'}
    
        )


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    pinned_graph_version_id = Column(UUID(as_uuid=True), ForeignKey("graph_versions.id", ondelete="RESTRICT"), nullable=True)
    current_chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    last_activity_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Chapter(Base):
    __tablename__ = "chapters"
    __table_args__ = (
    
            CheckConstraint('chapter_number > 0', name='chk_chapter_number'),
    
            CheckConstraint('estimated_minutes IS NULL OR estimated_minutes > 0', name='chk_estimated_minutes'),
    
            ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE', name='chapters_book_id_fkey'),
    
            PrimaryKeyConstraint('id', name='chapters_pkey'),
    
            UniqueConstraint('book_id', 'chapter_number', name='uq_book_chapter_number'),
    
            Index('idx_chapters_book_id', 'book_id'),
    
            Index('idx_chapters_number', 'book_id', 'chapter_number'),
    
            {'comment': 'Book chapters. Structural prior for concept extraction and '
    
                    'chunking.'}
    
        )


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
    __table_args__ = (
    
            ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE', name='book_uploads_book_id_fkey'),
    
            ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='book_uploads_user_id_fkey'),
    
            PrimaryKeyConstraint('id', name='book_uploads_pkey')
    
        )


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    original_filename = Column(Text, nullable=False)
    storage_path = Column(Text, nullable=False)
    file_size_bytes = Column(BigInteger)
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
    __table_args__ = (
    
            ForeignKeyConstraint(['graph_version_id'], ['graph_versions.id'], ondelete='CASCADE', name='graph_repair_log_graph_version_id_fkey'),
    
            PrimaryKeyConstraint('id', name='graph_repair_log_pkey')
    
        )


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
