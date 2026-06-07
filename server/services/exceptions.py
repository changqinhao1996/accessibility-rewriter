"""
Custom exception types for the rewrite service layer.
"""


class StyleRewriterError(Exception):
    """Base exception for StyleRewriter adapter errors."""

    pass


class UnclearTextError(StyleRewriterError):
    """Raised when the source text is too unclear to rewrite safely."""

    def __init__(self, message: str = "The text is too unclear to rewrite safely."):
        self.message = message
        super().__init__(self.message)


class ServiceUnavailableError(StyleRewriterError):
    """Raised when the StyleRewriter service is unreachable."""

    def __init__(
        self,
        message: str = "The rewriting service is currently unavailable.",
    ):
        self.message = message
        super().__init__(self.message)


class SourceTextEmptyError(ValueError):
    """Raised when the source text is empty or whitespace-only."""

    def __init__(
        self,
        message: str = "Please enter or select source text before rewriting.",
    ):
        self.message = message
        super().__init__(self.message)


class ReadingLevelRequiredError(ValueError):
    """Raised when no reading level is selected."""

    def __init__(
        self,
        message: str = "Please select a target reading level.",
    ):
        self.message = message
        super().__init__(self.message)
