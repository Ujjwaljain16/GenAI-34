"""ingestion_batching

Revision ID: de54f380a89e
Revises: 762017ca7505
Create Date: 2026-06-07

Adds three new tables for the batched, resumable ingestion pipeline:
  - raw_concepts              — per-chunk LLM extraction output; checkpoint so
                                the worker can skip already-processed chunks.
  - relationship_candidates   — all (src, tgt) pairs to evaluate; generated
                                once, processed incrementally.
  - evaluated_pairs           — immutable audit log of every LLM relationship
                                judgement (EDGE_CREATED | NO_RELATIONSHIP |
                                FAILED). Keeps graph_model clean — no NONE edges.

Also extends graph_build_jobs with five progress/resilience columns:
  - current_stage             — human-readable stage name for resumability.
  - current_offset            — offset within the current stage for fine-grained
                                resume.
  - retry_count               — number of automatic retries so far.
  - last_error                — last exception message.
  - next_retry_at             — when the worker should attempt a retry.

And extends the graph_build_status enum with the full stage set:
  CHUNKING, CANONICALIZING, EXTRACTING_RELATIONSHIPS, REPAIRING, PUBLISHING.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'de54f380a89e'
down_revision = '762017ca7505'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Extend the graph_build_status ENUM ──────────────────────────────────
    # PostgreSQL requires ALTER TYPE outside a transaction for most drivers,
    # so we use execute() with explicit COMMIT via a raw DBAPI connection.
    # We guard each ADD VALUE with IF NOT EXISTS (PG 9.6+).
    new_values = [
        'CHUNKING',
        'CANONICALIZING',
        'EXTRACTING_RELATIONSHIPS',
        'REPAIRING',
        'PUBLISHING',
    ]
    for val in new_values:
        op.execute(f"ALTER TYPE graph_build_status ADD VALUE IF NOT EXISTS '{val}'")

    # ── New columns on graph_build_jobs ─────────────────────────────────────
    op.add_column('graph_build_jobs',
        sa.Column('current_stage', sa.String(50), nullable=True))
    op.add_column('graph_build_jobs',
        sa.Column('current_offset', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('graph_build_jobs',
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('graph_build_jobs',
        sa.Column('last_error', sa.Text(), nullable=True))
    op.add_column('graph_build_jobs',
        sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True))

    # ── raw_concepts ─────────────────────────────────────────────────────────
    op.create_table(
        'raw_concepts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('graph_version_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('graph_versions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_chunk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('difficulty_level', sa.Integer(), nullable=False),
        sa.Column('subtopics', postgresql.JSONB(), nullable=False,
                  server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_raw_concepts_version', 'raw_concepts', ['graph_version_id'])
    op.create_index('ix_raw_concepts_chunk', 'raw_concepts', ['source_chunk_id'])

    # ── relationship_candidates ───────────────────────────────────────────────
    op.create_table(
        'relationship_candidates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('graph_version_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('graph_versions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_concept_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('concepts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_concept_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('concepts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='PENDING'),
        sa.Column('confidence', sa.Numeric(5, 4), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_rel_candidates_version_status',
                    'relationship_candidates', ['graph_version_id', 'status'])

    # ── evaluated_pairs ───────────────────────────────────────────────────────
    op.create_table(
        'evaluated_pairs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('graph_version_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('graph_versions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_concept_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('concepts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_concept_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('concepts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('confidence', sa.Numeric(5, 4), nullable=True),
        sa.Column('llm_version', sa.String(50), nullable=True),
        sa.Column('evaluated_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_evaluated_pairs_version', 'evaluated_pairs', ['graph_version_id'])
    op.create_unique_constraint(
        'uq_evaluated_pairs_version_src_tgt',
        'evaluated_pairs',
        ['graph_version_id', 'source_concept_id', 'target_concept_id'],
    )


def downgrade() -> None:
    op.drop_table('evaluated_pairs')
    op.drop_table('relationship_candidates')
    op.drop_table('raw_concepts')

    op.drop_column('graph_build_jobs', 'next_retry_at')
    op.drop_column('graph_build_jobs', 'last_error')
    op.drop_column('graph_build_jobs', 'retry_count')
    op.drop_column('graph_build_jobs', 'current_offset')
    op.drop_column('graph_build_jobs', 'current_stage')

    # Note: PostgreSQL does not support removing values from an ENUM.
    # Downgrade cannot reverse the ALTER TYPE ADD VALUE statements.
