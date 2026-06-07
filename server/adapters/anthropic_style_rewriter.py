"""
Real StyleRewriter adapter backed by Anthropic Claude.
"""

import anthropic

from adapters.style_rewriter_port import StyleRewriterPort
from services.exceptions import ServiceUnavailableError, UnclearTextError


_SYSTEM_PROMPT = (
    "You are an expert plain-language editor. "
    "Rewrite the user's text so it matches the specified reading level. "
    "Preserve the original meaning and all factual content. "
    "Return ONLY the rewritten text — no commentary, no preamble. "
    "If the text is too ambiguous or unclear to rewrite safely, "
    "respond with exactly: UNCLEAR_TEXT_ERROR"
)


class AnthropicStyleRewriter(StyleRewriterPort):
    """Calls the Anthropic Claude API to rewrite text."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def rewrite(self, text: str, target_level: str) -> str:
        """
        Rewrite text to the target reading level using Claude.

        Raises:
            UnclearTextError: If Claude determines the text is too unclear.
            ServiceUnavailableError: On network or API errors.
        """
        try:
            message = await self._client.messages.create(
                model=self._model,
                max_tokens=2048,
                system=_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Target reading level: {target_level}\n\n"
                            f"Text to rewrite:\n{text}"
                        ),
                    }
                ],
            )

            rewritten = message.content[0].text.strip()

            if "UNCLEAR_TEXT_ERROR" in rewritten:
                raise UnclearTextError()

            return rewritten

        except UnclearTextError:
            raise
        except anthropic.APIConnectionError as exc:
            raise ServiceUnavailableError() from exc
        except anthropic.APIStatusError as exc:
            if exc.status_code >= 500:
                raise ServiceUnavailableError() from exc
            raise
        except Exception as exc:
            raise ServiceUnavailableError() from exc
