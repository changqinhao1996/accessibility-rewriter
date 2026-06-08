"""
Fake VisionAnalyzer adapter for acceptance testing.
Returns canned alt text and supports complex/outage simulation.
"""

from adapters.vision_analyzer_port import VisionAnalyzerPort, VisionResult
from services.exceptions import ServiceUnavailableError


class FakeVisionAnalyzer(VisionAnalyzerPort):
    """Test double for VisionAnalyzerPort.

    Supports multiple modes:
    - Default: returns a canned alt text
    - Complex: returns is_too_complex=True
    - Outage: raises ServiceUnavailableError
    - Contextual: incorporates purpose note keywords
    - Regenerate: returns a different text on each call
    """

    def __init__(self):
        self.simulate_outage: bool = False
        self.simulate_complex: bool = False
        self._call_count: int = 0
        self._canned_responses: list[str] = [
            "Scenic landscape with green hills and blue sky",
            "Rolling meadow under cloudy skies with distant mountains",
            "Peaceful countryside with verdant fields",
        ]

    async def analyze_image(
        self,
        image_data: bytes,
        mime_type: str,
        purpose_note: str | None = None,
        filename: str | None = None,
    ) -> VisionResult:
        """Return a canned result based on the configured mode."""
        self._call_count += 1

        # Outage simulation
        if self.simulate_outage:
            raise ServiceUnavailableError()

        # Complex image simulation
        if self.simulate_complex:
            return VisionResult(alt_text="", is_too_complex=True)

        # Contextual: incorporate purpose note keywords
        if purpose_note:
            return VisionResult(
                alt_text=f"Contextual description relating to {purpose_note}"[:125],
                is_too_complex=False,
            )

        # Filename-based responses for specific test fixtures
        if filename:
            fname_lower = filename.lower()
            if "apple" in fname_lower:
                return VisionResult(
                    alt_text="Red apple on a white table",
                    is_too_complex=False,
                )
            if "barchart" in fname_lower or "chart" in fname_lower:
                return VisionResult(
                    alt_text="Bar chart showing quarterly sales data",
                    is_too_complex=False,
                )

        # Default: return canned response (cycles for regeneration)
        idx = (self._call_count - 1) % len(self._canned_responses)
        return VisionResult(
            alt_text=self._canned_responses[idx],
            is_too_complex=False,
        )
