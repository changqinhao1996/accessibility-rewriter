"""
Database helper utilities for UC3 acceptance tests.
Uses synchronous psycopg2 to avoid asyncio event loop conflicts with Playwright.
"""

import os
import shutil
import uuid
from datetime import datetime, timezone

import psycopg2

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://qinhaochang@localhost:5432/accessibility_rewriter",
)

SEED_DOC_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")
UPLOADS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "uploads"
)


def _get_conn():
    """Create a synchronous psycopg2 connection."""
    return psycopg2.connect(DATABASE_URL)


def reset_images_table() -> None:
    """Truncate the images table."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE images CASCADE")
        conn.commit()
    finally:
        conn.close()


def ensure_seed_document_exists() -> uuid.UUID:
    """Ensure the seed document exists (upsert)."""
    conn = _get_conn()
    try:
        now = datetime.now(timezone.utc)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents (id, title, content, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (str(SEED_DOC_ID), "Test Document", "Test content for UC3", now, now),
            )
        conn.commit()
        return SEED_DOC_ID
    finally:
        conn.close()


def seed_image(
    filename: str = "landscape.png",
    alt_text: str | None = None,
    alt_text_status: str = "missing",
    image_id: uuid.UUID | None = None,
) -> uuid.UUID:
    """Seed an image record and copy the fixture file to uploads."""
    if image_id is None:
        image_id = uuid.uuid4()

    # Copy fixture file to uploads directory
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    fixture_path = os.path.join(FIXTURES_DIR, filename)
    ext = os.path.splitext(filename)[1]
    saved_name = f"{image_id}{ext}"
    dest_path = os.path.join(UPLOADS_DIR, saved_name)

    if os.path.exists(fixture_path):
        shutil.copy2(fixture_path, dest_path)
    else:
        # Create a minimal placeholder
        with open(dest_path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    conn = _get_conn()
    try:
        now = datetime.now(timezone.utc)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO images (id, document_id, filename, file_path, mime_type,
                                    alt_text, alt_text_status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(image_id),
                    str(SEED_DOC_ID),
                    filename,
                    dest_path,
                    "image/png" if ext == ".png" else "image/jpeg",
                    alt_text,
                    alt_text_status,
                    now,
                    now,
                ),
            )
        conn.commit()
        return image_id
    finally:
        conn.close()


def get_image_record(image_id: uuid.UUID) -> dict | None:
    """Fetch an image record by ID."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, alt_text, alt_text_status FROM images WHERE id = %s",
                (str(image_id),),
            )
            row = cur.fetchone()
            if row:
                return {"id": row[0], "alt_text": row[1], "alt_text_status": row[2]}
            return None
    finally:
        conn.close()


def get_all_images() -> list[dict]:
    """Fetch all image records."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, alt_text, alt_text_status FROM images ORDER BY created_at"
            )
            rows = cur.fetchall()
            return [
                {"id": row[0], "alt_text": row[1], "alt_text_status": row[2]}
                for row in rows
            ]
    finally:
        conn.close()


def get_image_count() -> int:
    """Return the number of images in the database."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM images")
            return cur.fetchone()[0]
    finally:
        conn.close()
