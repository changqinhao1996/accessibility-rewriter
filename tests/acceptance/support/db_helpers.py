"""
Database helper utilities for acceptance tests.
Provides seed, reset, and query functions using direct asyncpg connections.
"""

import os
import uuid
from datetime import datetime, timezone

import asyncpg

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://qinhaochang@localhost:5432/accessibility_rewriter",
)

# Fixed UUID for the seed document — deterministic across test runs.
SEED_DOC_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")

DEFAULT_CONTENT = (
    "Photosynthesis is the biochemical process by which chloroplasts in plant cells "
    "convert light energy into adenosine triphosphate, facilitating the synthesis of "
    "glucose from carbon dioxide and water."
)


async def _get_conn() -> asyncpg.Connection:
    """Create a raw asyncpg connection."""
    return await asyncpg.connect(DATABASE_URL)


async def reset_db() -> None:
    """Truncate all test tables."""
    conn = await _get_conn()
    try:
        await conn.execute("TRUNCATE document_versions CASCADE")
        await conn.execute("TRUNCATE documents CASCADE")
    finally:
        await conn.close()


async def seed_document(
    doc_id: uuid.UUID | None = None,
    title: str = "Photosynthesis",
    content: str | None = None,
) -> uuid.UUID:
    """Insert a seed document and return its ID."""
    if doc_id is None:
        doc_id = SEED_DOC_ID
    if content is None:
        content = DEFAULT_CONTENT

    conn = await _get_conn()
    try:
        now = datetime.now(timezone.utc)
        await conn.execute(
            """
            INSERT INTO documents (id, title, content, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (id) DO UPDATE SET content = $3, updated_at = $5
            """,
            doc_id,
            title,
            content,
            now,
            now,
        )
        return doc_id
    finally:
        await conn.close()


async def seed_version(
    document_id: uuid.UUID,
    version_number: int,
    content: str = "Default version content",
    reading_level: str = "Original",
    author: str = "ContentDesigner",
) -> uuid.UUID:
    """Insert a seed document version and return its ID."""
    version_id = uuid.uuid4()
    conn = await _get_conn()
    try:
        await conn.execute(
            """
            INSERT INTO document_versions
                (id, document_id, version_number, content, reading_level, author, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            version_id,
            document_id,
            version_number,
            content,
            reading_level,
            author,
            datetime.now(timezone.utc),
        )
        return version_id
    finally:
        await conn.close()


async def get_version_count(document_id: uuid.UUID) -> int:
    """Return the number of versions for a document."""
    conn = await _get_conn()
    try:
        row = await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM document_versions WHERE document_id = $1",
            document_id,
        )
        return row["cnt"]
    finally:
        await conn.close()


async def get_versions(document_id: uuid.UUID) -> list[dict]:
    """Return all versions for a document as a list of dicts."""
    conn = await _get_conn()
    try:
        rows = await conn.fetch(
            """
            SELECT id, document_id, version_number, content,
                   reading_level, author, created_at
            FROM document_versions
            WHERE document_id = $1
            ORDER BY version_number
            """,
            document_id,
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_latest_version(document_id: uuid.UUID) -> dict | None:
    """Return the most recent version for a document."""
    conn = await _get_conn()
    try:
        row = await conn.fetchrow(
            """
            SELECT id, document_id, version_number, content,
                   reading_level, author, created_at
            FROM document_versions
            WHERE document_id = $1
            ORDER BY version_number DESC
            LIMIT 1
            """,
            document_id,
        )
        return dict(row) if row else None
    finally:
        await conn.close()
