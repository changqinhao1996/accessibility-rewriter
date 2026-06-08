"""
AltTextService — orchestrates alt text generation, approval, and cancellation.
"""

import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.vision_analyzer_port import VisionAnalyzerPort, VisionResult
from models.image import Image


class AltTextService:
    """Application service for UC3: GenerateImageAltText."""

    def __init__(self, vision_analyzer: VisionAnalyzerPort):
        self._vision_analyzer = vision_analyzer

    async def generate_alt_text(
        self, image: Image, purpose_note: str | None = None
    ) -> VisionResult:
        """
        Generate alt text for the given image.

        Returns:
            VisionResult with generated alt text and complexity flag.
        """
        # Read image file from disk
        image_path = image.file_path
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        with open(image_path, "rb") as f:
            image_data = f.read()

        result = await self._vision_analyzer.analyze_image(
            image_data=image_data,
            mime_type=image.mime_type,
            purpose_note=purpose_note,
            filename=image.filename,
        )

        return result

    async def approve_alt_text(
        self, session: AsyncSession, image_id: str, alt_text: str
    ) -> Image:
        """
        Approve and persist alt text for an image.

        Sets alt_text_status to 'described'.
        """
        result = await session.execute(
            select(Image).where(Image.id == image_id)
        )
        image = result.scalar_one()
        image.alt_text = alt_text
        image.alt_text_status = "described"
        await session.flush()
        return image

    async def cancel_generation(
        self, session: AsyncSession, image_id: str
    ) -> Image:
        """
        Cancel alt text generation — resets to 'missing'.
        """
        result = await session.execute(
            select(Image).where(Image.id == image_id)
        )
        image = result.scalar_one()
        image.alt_text = None
        image.alt_text_status = "missing"
        await session.flush()
        return image
