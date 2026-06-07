"""
Pydantic schemas for the rewrite API endpoints.
"""

from pydantic import BaseModel


class RewriteRequest(BaseModel):
    """Request body for POST /api/rewrite."""

    text: str
    reading_level: str


class RewriteResult(BaseModel):
    """Response body for POST /api/rewrite."""

    original_text: str
    rewritten_text: str
    reading_grade: float
    target_reading_level: str
