"""
ORM model for Images.
Supports UC3: GenerateImageAltText.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class Image(Base):
    """An image attached to a document, with optional alt text."""

    __tablename__ = "images"
    __table_args__ = (
        CheckConstraint(
            "alt_text_status IN ('missing', 'pending', 'described')",
            name="ck_image_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    filename = Column(String(500), nullable=False)
    file_path = Column(Text, nullable=False)
    mime_type = Column(String(100), nullable=False)
    alt_text = Column(Text, nullable=True)
    alt_text_status = Column(String(20), nullable=False, default="missing")
    purpose_note = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    document = relationship("Document", backref="images")

    def __repr__(self) -> str:
        return f"<Image id={self.id} filename={self.filename!r} status={self.alt_text_status}>"
