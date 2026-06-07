"""
API routes for document and document-version endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories.document_repository import DocumentRepository, VersionRepository
from schemas.document import DocumentOut, SaveVersionRequest, VersionOut
from services.rewrite_service import RewriteService

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    db: AsyncSession = Depends(get_db),
) -> list[DocumentOut]:
    """Fetch all documents."""
    docs = await DocumentRepository.get_all(db)
    return [DocumentOut.model_validate(d) for d in docs]


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DocumentOut:
    """Fetch a document by ID."""
    doc = await DocumentRepository.get_by_id(db, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentOut.model_validate(doc)


@router.get("/{document_id}/versions", response_model=list[VersionOut])
async def get_versions(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[VersionOut]:
    """Fetch all versions for a document."""
    doc = await DocumentRepository.get_by_id(db, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    versions = await VersionRepository.get_versions(db, document_id)
    return [VersionOut.model_validate(v) for v in versions]


@router.post(
    "/{document_id}/versions",
    response_model=VersionOut,
    status_code=201,
)
async def save_version(
    document_id: UUID,
    body: SaveVersionRequest,
    db: AsyncSession = Depends(get_db),
) -> VersionOut:
    """Save a new version of a document."""
    doc = await DocumentRepository.get_by_id(db, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    version = await RewriteService.save_version(
        db=db,
        document_id=document_id,
        content=body.content,
        reading_level=body.reading_level,
        author=body.author,
    )
    return VersionOut.model_validate(version)
