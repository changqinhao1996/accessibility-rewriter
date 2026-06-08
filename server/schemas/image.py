"""
Pydantic schemas for the Image API endpoints (UC3: GenerateImageAltText).
"""

from pydantic import BaseModel


class ImageOut(BaseModel):
    """Serialized image record."""

    id: str
    document_id: str
    filename: str
    image_url: str
    alt_text: str | None
    alt_text_status: str
    purpose_note: str | None

    class Config:
        from_attributes = True


class GenerateRequest(BaseModel):
    """Request body for alt text generation."""

    purpose_note: str | None = None


class GenerateResult(BaseModel):
    """Result of alt text generation."""

    alt_text: str
    is_too_complex: bool


class ApproveRequest(BaseModel):
    """Request body for approving alt text."""

    alt_text: str
