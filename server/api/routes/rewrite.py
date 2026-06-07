"""
API routes for the rewrite endpoint (POST /api/rewrite).
"""

from fastapi import APIRouter, Depends, HTTPException

from schemas.rewrite import RewriteRequest, RewriteResult
from services.exceptions import (
    ReadingLevelRequiredError,
    ServiceUnavailableError,
    SourceTextEmptyError,
    UnclearTextError,
)
from services.rewrite_service import RewriteService

router = APIRouter(prefix="/api", tags=["rewrite"])


def get_rewrite_service() -> RewriteService:
    """Dependency placeholder — overridden in main.py."""
    raise NotImplementedError("RewriteService dependency not configured")


@router.post("/rewrite", response_model=RewriteResult)
async def rewrite_text(
    body: RewriteRequest,
    service: RewriteService = Depends(get_rewrite_service),
) -> RewriteResult:
    """
    Rewrite text to a target reading level.

    Returns 200 on success, 422 for validation errors,
    502 if text is too unclear, 503 if the service is down.
    """
    try:
        return await service.rewrite_text(body.text, body.reading_level)
    except SourceTextEmptyError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    except ReadingLevelRequiredError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    except UnclearTextError as exc:
        raise HTTPException(status_code=502, detail=exc.message) from exc
    except ServiceUnavailableError as exc:
        raise HTTPException(status_code=503, detail=exc.message) from exc
