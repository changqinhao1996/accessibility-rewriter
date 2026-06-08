"""
Real VisionAnalyzer adapter backed by Anthropic Claude Vision.
"""

import base64
import json

import anthropic

from adapters.vision_analyzer_port import VisionAnalyzerPort, VisionResult
from services.exceptions import ServiceUnavailableError

_SYSTEM_PROMPT = (
    "You are a WCAG 2.1 accessibility expert. Generate alt text for the provided image.\n\n"
    "Rules:\n"
    "- Describe ONLY what is visible in the image — never invent or assume elements\n"
    "- Keep the description concise: at most 125 characters\n"
    "- Do NOT start with 'image of', 'picture of', 'photo of', or similar prefixes\n"
    "- Be specific and descriptive\n"
    "- If the image is too complex (dense charts, infographics with many data points), "
    'respond with: {"alt_text": "", "is_too_complex": true}\n\n'
    "If a purpose note is provided, use it to give context-appropriate descriptions.\n\n"
    'Respond in JSON only: {"alt_text": "...", "is_too_complex": false}'
)


class AnthropicVisionAnalyzer(VisionAnalyzerPort):
    """Calls the Anthropic Claude Vision API to generate alt text."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def analyze_image(
        self,
        image_data: bytes,
        mime_type: str,
        purpose_note: str | None = None,
        filename: str | None = None,
    ) -> VisionResult:
        """
        Analyze an image using Claude Vision and return WCAG-compliant alt text.

        Raises:
            ServiceUnavailableError: On network or API errors.
        """
        try:
            image_b64 = base64.standard_b64encode(image_data).decode("utf-8")

            user_content = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mime_type,
                        "data": image_b64,
                    },
                },
                {
                    "type": "text",
                    "text": (
                        f"Purpose note: {purpose_note}\n\nGenerate alt text for this image."
                        if purpose_note
                        else "Generate alt text for this image."
                    ),
                },
            ]

            message = await self._client.messages.create(
                model=self._model,
                max_tokens=256,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_content}],
            )

            raw = message.content[0].text.strip()

            # Parse JSON response
            try:
                data = json.loads(raw)
                return VisionResult(
                    alt_text=data.get("alt_text", ""),
                    is_too_complex=data.get("is_too_complex", False),
                )
            except json.JSONDecodeError:
                # If Claude didn't return JSON, use raw text as alt text
                return VisionResult(alt_text=raw[:125], is_too_complex=False)

        except anthropic.APIConnectionError as exc:
            raise ServiceUnavailableError() from exc
        except anthropic.APIStatusError as exc:
            if exc.status_code >= 500:
                raise ServiceUnavailableError() from exc
            raise
        except Exception as exc:
            raise ServiceUnavailableError() from exc
