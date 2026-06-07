"""
Abstract interface for the StyleRewriter adapter.
All adapters (real and test-double) implement this port.
"""

from abc import ABC, abstractmethod


class StyleRewriterPort(ABC):
    """Port defining how the service layer communicates with a text rewriter."""

    @abstractmethod
    async def rewrite(self, text: str, target_level: str) -> str:
        """
        Rewrite the given text to the specified reading level.

        Args:
            text: The source text to rewrite.
            target_level: The target reading level label (e.g., "Plain (Grades 6–8)").

        Returns:
            The rewritten text as a string.

        Raises:
            UnclearTextError: If the text is too unclear to rewrite safely.
            ServiceUnavailableError: If the rewriting service is unreachable.
        """
