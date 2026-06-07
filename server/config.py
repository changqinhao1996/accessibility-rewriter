"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env file or environment."""

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/accessibility_rewriter"

    # Anthropic Claude API
    ANTHROPIC_API_KEY: str = ""

    # Adapter toggle: set to "true" to force FakeStyleRewriter (tests/offline dev).
    # When empty, auto-detects: uses fake if ANTHROPIC_API_KEY is missing.
    USE_FAKE_REWRITER: str = ""

    # Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # Frontend origin (for CORS)
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    @property
    def should_use_fake_rewriter(self) -> bool:
        """Determine whether to use FakeStyleRewriter."""
        if self.USE_FAKE_REWRITER.lower() in ("true", "1", "yes"):
            return True
        if self.USE_FAKE_REWRITER.lower() in ("false", "0", "no"):
            return False
        # Auto-detect: use fake if no API key is configured
        return not self.ANTHROPIC_API_KEY

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


settings = Settings()
