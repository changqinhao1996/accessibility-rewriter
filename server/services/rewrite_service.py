"""
RewriteService — business logic for UC1: RewriteTextToReadingLevel.
"""

from uuid import UUID

import textstat
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.style_rewriter_port import StyleRewriterPort
from models.document import DocumentVersion
from repositories.document_repository import VersionRepository
from schemas.rewrite import RewriteResult
from services.exceptions import ReadingLevelRequiredError, SourceTextEmptyError

# Allowed reading levels and their target grade midpoints.
READING_LEVELS: dict[str, float] = {
    "Very Simple (Grades 1–3)": 2,
    "Simple (Grades 4–5)": 4.5,
    "Plain (Grades 6–8)": 7,
    "Standard (Grades 9–12)": 10.5,
    "Technical (Grade 13+)": 14,
}


class RewriteService:
    """Orchestrates text rewriting and version persistence."""

    def __init__(self, style_rewriter: StyleRewriterPort) -> None:
        self._style_rewriter = style_rewriter

    async def rewrite_text(self, text: str, reading_level: str) -> RewriteResult:
        """
        Validate inputs, call the StyleRewriter, and return the result.

        Raises:
            SourceTextEmptyError: If text is empty or whitespace-only.
            ReadingLevelRequiredError: If reading_level is missing or invalid.
            UnclearTextError: Propagated from the adapter.
            ServiceUnavailableError: Propagated from the adapter.
        """
        # Validation
        if not text or not text.strip():
            raise SourceTextEmptyError()

        if not reading_level or reading_level not in READING_LEVELS:
            raise ReadingLevelRequiredError()

        # Delegate to the adapter
        rewritten = await self._style_rewriter.rewrite(text, reading_level)

        # Measure the reading grade of the output
        reading_grade = textstat.flesch_kincaid_grade(rewritten)

        return RewriteResult(
            original_text=text,
            rewritten_text=rewritten,
            reading_grade=reading_grade,
            target_reading_level=reading_level,
        )

    @staticmethod
    async def save_version(
        db: AsyncSession,
        document_id: UUID,
        content: str,
        reading_level: str,
        author: str,
    ) -> DocumentVersion:
        """
        Create a new append-only version for the given document.

        Returns:
            The newly created DocumentVersion.
        """
        next_num = await VersionRepository.get_next_version_number(db, document_id)

        version = DocumentVersion(
            document_id=document_id,
            version_number=next_num,
            content=content,
            reading_level=reading_level,
            author=author,
        )

        return await VersionRepository.create(db, version)
