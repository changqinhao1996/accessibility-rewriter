"""uc1_create_documents_and_versions

Revision ID: e3c651410f9e
Revises: 
Create Date: 2026-06-06 15:35:04.134720
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e3c651410f9e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop legacy Prisma tables that conflict with the new schema
    # (order matters due to FK constraints)
    for table in [
        'content_flags', 'content_scan_reports', 'diff_segments',
        'version_comparisons', 'compliance_reports', 'remediation_logs',
        'audit_reports', 'readability_analyses', 'rewrite_suggestions',
        'alt_text_suggestions', 'document_images',
    ]:
        op.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')

    op.execute('DROP TABLE IF EXISTS "documents" CASCADE')
    op.execute('DROP TABLE IF EXISTS "guidelines" CASCADE')
    op.execute('DROP TABLE IF EXISTS "guideline_configs" CASCADE')
    op.execute('DROP TABLE IF EXISTS "culture_profiles" CASCADE')
    op.execute('DROP TABLE IF EXISTS "_prisma_migrations" CASCADE')

    # Create UC1 tables
    op.create_table(
        'documents',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'document_versions',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('reading_level', sa.String(length=100), nullable=False),
        sa.Column('author', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id', 'version_number', name='uq_doc_version'),
    )


def downgrade() -> None:
    op.drop_table('document_versions')
    op.drop_table('documents')
