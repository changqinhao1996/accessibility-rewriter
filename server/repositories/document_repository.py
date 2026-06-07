"""
Repository for Document and DocumentVersion database operations.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.document import Document, DocumentVersion


class DocumentRepository:
    """Data-access methods for the documents table."""

    @staticmethod
    async def get_by_id(db: AsyncSession, document_id: UUID) -> Document | None:
        """Fetch a document by primary key."""
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> list[Document]:
        """Fetch all documents, ordered by creation date."""
        result = await db.execute(
            select(Document).order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id_with_versions(
        db: AsyncSession, document_id: UUID
    ) -> Document | None:
        """Fetch a document with all its versions eagerly loaded."""
        result = await db.execute(
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.versions))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, document: Document) -> Document:
        """Insert a new document."""
        db.add(document)
        await db.flush()
        return document


class VersionRepository:
    """Data-access methods for the document_versions table."""

    @staticmethod
    async def get_versions(
        db: AsyncSession, document_id: UUID
    ) -> list[DocumentVersion]:
        """Fetch all versions for a document, ordered by version_number."""
        result = await db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_version_count(db: AsyncSession, document_id: UUID) -> int:
        """Return the count of versions for a document."""
        result = await db.execute(
            select(func.count())
            .select_from(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
        )
        return result.scalar_one()

    @staticmethod
    async def get_next_version_number(db: AsyncSession, document_id: UUID) -> int:
        """Calculate the next version number for a document."""
        result = await db.execute(
            select(func.coalesce(func.max(DocumentVersion.version_number), 0))
            .where(DocumentVersion.document_id == document_id)
        )
        return result.scalar_one() + 1

    @staticmethod
    async def create(
        db: AsyncSession, version: DocumentVersion
    ) -> DocumentVersion:
        """Insert a new document version."""
        db.add(version)
        await db.flush()
        return version
