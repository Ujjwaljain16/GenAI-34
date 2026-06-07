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
