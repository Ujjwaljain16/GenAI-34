import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from app.models.base import Base


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), nullable=True)
    canonical_concept_id = Column(UUID(as_uuid=True), nullable=True)
    name = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    learning_objective = Column(Text, nullable=True)
    difficulty_level = Column(Integer, nullable=False)
    estimated_minutes = Column(Integer, nullable=True)
    graph_version = Column(Integer, nullable=False, default=1)
    metadata_ = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ConceptEdge(Base):
    __tablename__ = "concept_edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    graph_version = Column(Integer, nullable=False, default=1)
    from_concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    to_concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    edge_type = Column(ENUM('PREREQUISITE', 'RELATED', name='edge_type', create_type=False), nullable=False, default='PREREQUISITE')
    confidence = Column(Numeric(5, 4), nullable=False, default=0.5)
    weight = Column(Numeric(5, 4), nullable=False, default=1.0)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RawConcept(Base):
    __tablename__ = "raw_concepts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    graph_version_id = Column(UUID(as_uuid=True), ForeignKey("graph_versions.id", ondelete="CASCADE"), nullable=False)
    source_chunk_id = Column(UUID(as_uuid=True), nullable=False) # Not FK to avoid NoReferencedTableError since SourceChunk model is missing
    name = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    difficulty_level = Column(Integer, nullable=False)
    subtopics = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RelationshipCandidate(Base):
    __tablename__ = "relationship_candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    graph_version_id = Column(UUID(as_uuid=True), ForeignKey("graph_versions.id", ondelete="CASCADE"), nullable=False)
    source_concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    target_concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False, default="PENDING")
    confidence = Column(Numeric(5, 4), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class EvaluatedPair(Base):
    __tablename__ = "evaluated_pairs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    graph_version_id = Column(UUID(as_uuid=True), ForeignKey("graph_versions.id", ondelete="CASCADE"), nullable=False)
    source_concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    target_concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False)
    confidence = Column(Numeric(5, 4), nullable=True)
    llm_version = Column(String(50), nullable=True)
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class SourceChunk(Base):
    __tablename__ = "source_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"))
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer)
    page_start = Column(Integer)
    page_end = Column(Integer)
    metadata_ = Column("metadata", JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ConceptChunk(Base):
    __tablename__ = "concept_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("source_chunks.id", ondelete="CASCADE"), nullable=False)
    relevance_score = Column(Numeric(5, 4))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
