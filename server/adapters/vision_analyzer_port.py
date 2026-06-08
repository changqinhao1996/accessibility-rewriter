"""
Abstract interface for the VisionAnalyzer adapter.
All adapters (real and test-double) implement this port.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class VisionResult:
    """Result of an image analysis for alt text generation."""

    alt_text: str  # Generated alt text (≤ 125 chars recommended)
    is_too_complex: bool  # True if image can't be described confidently


class VisionAnalyzerPort(ABC):
    """Port defining how the service layer communicates with a vision analyzer."""

    @abstractmethod
    async def analyze_image(
        self,
        image_data: bytes,
        mime_type: str,
        purpose_note: str | None = None,
        filename: str | None = None,
    ) -> VisionResult:
        """
        Analyze an image and generate WCAG-compliant alt text.

        Args:
            image_data: The raw image bytes.
            mime_type: The MIME type (e.g., "image/png").
            purpose_note: Optional context note describing the image's purpose.
            filename: Optional filename hint for test adapters.

        Returns:
            VisionResult with the generated alt text and complexity flag.

        Raises:
            ServiceUnavailableError: If the vision service is unreachable.
        """
