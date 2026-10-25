"""add knowledge_chunks table with pgvector

Revision ID: a1b2c3d4e5f6
Revises: ce17a4b2f8d1
Create Date: 2026-10-21 14:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ce17a4b2f8d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    op.create_table(
        'knowledge_chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chunk', sa.Text(), nullable=False),
        sa.Column('contextual_header', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(384), nullable=False),
        sa.Column('meta', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index for vector similarity search (HNSW)
    op.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_embedding_hnsw ON knowledge_chunks USING hnsw (embedding vector_cosine_ops);")

    # Create index for metadata filtering
    op.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_meta_crop ON knowledge_chunks ((meta->>'crop'));")
    op.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_meta_source ON knowledge_chunks ((meta->>'source'));")
    op.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_meta_topic ON knowledge_chunks ((meta->>'topic'));")


def downgrade() -> None:
    op.drop_table('knowledge_chunks')
    op.execute("DROP EXTENSION IF EXISTS vector;")