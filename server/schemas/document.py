"""
Pydantic schemas for document and document-version API endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentOut(BaseModel):
    """Response schema for GET /api/documents/{id}."""

    id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SaveVersionRequest(BaseModel):
    """Request body for POST /api/documents/{id}/versions."""

    content: str
    reading_level: str
    author: str


class VersionOut(BaseModel):
    """Response schema for a document version."""

    id: UUID
    document_id: UUID
    version_number: int
    content: str
    reading_level: str
    author: str
    created_at: datetime

    model_config = {"from_attributes": True}
