"""
API routes for Image endpoints (UC3: GenerateImageAltText).

POST   /api/images/upload         — Upload image to document
GET    /api/images                 — List all images
POST   /api/images/{id}/generate   — Generate alt text
PUT    /api/images/{id}/approve    — Approve alt text
PUT    /api/images/{id}/cancel     — Cancel / discard
"""

import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.image import Image
from schemas.image import ApproveRequest, GenerateRequest, GenerateResult, ImageOut
from services.alttext_service import AltTextService
from services.exceptions import ServiceUnavailableError

router = APIRouter(prefix="/api", tags=["images"])

# ── Upload directory ─────────────────────────────────────────────────
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


# ── Dependency: AltTextService ───────────────────────────────────────
def get_alttext_service() -> AltTextService:
    """Placeholder — overridden by main.py DI."""
    raise NotImplementedError("AltTextService not injected")


# ── Routes ───────────────────────────────────────────────────────────


@router.post("/images/upload", response_model=ImageOut, status_code=201)
async def upload_image(
    file: UploadFile = File(...),
    document_id: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload an image file and create a database record."""
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. "
            f"Allowed: {', '.join(ALLOWED_MIME_TYPES)}",
        )

    # Save file to uploads directory
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename or "image.png")[1]
    saved_filename = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Create database record
    image = Image(
        document_id=document_id,
        filename=file.filename or "upload",
        file_path=file_path,
        mime_type=file.content_type,
        alt_text=None,
        alt_text_status="missing",
    )
    db.add(image)
    await db.flush()

    return ImageOut(
        id=str(image.id),
        document_id=str(image.document_id),
        filename=image.filename,
        image_url=f"/uploads/{saved_filename}",
        alt_text=image.alt_text,
        alt_text_status=image.alt_text_status,
        purpose_note=image.purpose_note,
    )


@router.get("/images", response_model=list[ImageOut])
async def list_images(db: AsyncSession = Depends(get_db)):
    """List all images with their alt text status."""
    result = await db.execute(select(Image).order_by(Image.created_at))
    images = result.scalars().all()
    return [
        ImageOut(
            id=str(img.id),
            document_id=str(img.document_id),
            filename=img.filename,
            image_url=f"/uploads/{os.path.basename(img.file_path)}" if img.file_path else "",
            alt_text=img.alt_text,
            alt_text_status=img.alt_text_status,
            purpose_note=img.purpose_note,
        )
        for img in images
    ]


@router.post("/images/{image_id}/generate", response_model=GenerateResult)
async def generate_alt_text(
    image_id: str,
    body: GenerateRequest,
    db: AsyncSession = Depends(get_db),
    service: AltTextService = Depends(get_alttext_service),
):
    """Generate alt text for an image using AI vision."""
    # Fetch the image
    result = await db.execute(select(Image).where(Image.id == image_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        vision_result = await service.generate_alt_text(
            image=image, purpose_note=body.purpose_note
        )
    except ServiceUnavailableError:
        raise HTTPException(
            status_code=503, detail="AI vision service is unavailable"
        )

    # Update status to pending
    image.alt_text_status = "pending"
    await db.flush()

    return GenerateResult(
        alt_text=vision_result.alt_text,
        is_too_complex=vision_result.is_too_complex,
    )


@router.put("/images/{image_id}/approve", response_model=ImageOut)
async def approve_alt_text(
    image_id: str,
    body: ApproveRequest,
    db: AsyncSession = Depends(get_db),
    service: AltTextService = Depends(get_alttext_service),
):
    """Approve and persist alt text for an image."""
    try:
        image = await service.approve_alt_text(
            session=db, image_id=image_id, alt_text=body.alt_text
        )
    except Exception:
        raise HTTPException(status_code=404, detail="Image not found")

    return ImageOut(
        id=str(image.id),
        document_id=str(image.document_id),
        filename=image.filename,
        image_url=f"/uploads/{os.path.basename(image.file_path)}" if image.file_path else "",
        alt_text=image.alt_text,
        alt_text_status=image.alt_text_status,
        purpose_note=image.purpose_note,
    )


@router.put("/images/{image_id}/cancel", response_model=ImageOut)
async def cancel_alt_text(
    image_id: str,
    db: AsyncSession = Depends(get_db),
    service: AltTextService = Depends(get_alttext_service),
):
    """Cancel alt text generation — reset to missing."""
    try:
        image = await service.cancel_generation(session=db, image_id=image_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Image not found")

    return ImageOut(
        id=str(image.id),
        document_id=str(image.document_id),
        filename=image.filename,
        image_url=f"/uploads/{os.path.basename(image.file_path)}" if image.file_path else "",
        alt_text=image.alt_text,
        alt_text_status=image.alt_text_status,
        purpose_note=image.purpose_note,
    )
