"""
Accessibility & Tone Rewriter — FastAPI Application Entry Point
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import analyze as analyze_router
from api.routes import documents as documents_router
from api.routes import images as images_router
from api.routes import rewrite as rewrite_router
from config import settings
from services.alttext_service import AltTextService
from services.rewrite_service import RewriteService

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Accessibility & Tone Rewriter",
    description="API for rewriting text to target reading levels, checking WCAG accessibility, and more.",
    version="0.2.0",
)

# CORS — allow the Vite dev server during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Dependency Injection ─────────────────────────────────────────────
# Choose the adapter based on configuration:
#   - Demo / production: real Anthropic adapters (needs ANTHROPIC_API_KEY)
#   - Tests / offline dev: Fake adapters (no API key required)

# --- UC1: Style Rewriter ---
if settings.should_use_fake_rewriter:
    from adapters.fake_style_rewriter import FakeStyleRewriter

    _style_rewriter = FakeStyleRewriter()
    logger.warning(
        "Using FakeStyleRewriter — set ANTHROPIC_API_KEY in .env for real Claude rewrites"
    )
else:
    from adapters.anthropic_style_rewriter import AnthropicStyleRewriter

    _style_rewriter = AnthropicStyleRewriter(api_key=settings.ANTHROPIC_API_KEY)
    logger.info("Using AnthropicStyleRewriter (Claude API)")

_rewrite_service = RewriteService(style_rewriter=_style_rewriter)


def _get_rewrite_service() -> RewriteService:
    return _rewrite_service


app.dependency_overrides[rewrite_router.get_rewrite_service] = _get_rewrite_service

# --- UC3: Vision Analyzer ---
if settings.should_use_fake_rewriter:
    from adapters.fake_vision_analyzer import FakeVisionAnalyzer

    _vision_analyzer = FakeVisionAnalyzer()
    logger.warning("Using FakeVisionAnalyzer for alt text generation")
else:
    from adapters.anthropic_vision_analyzer import AnthropicVisionAnalyzer

    _vision_analyzer = AnthropicVisionAnalyzer(api_key=settings.ANTHROPIC_API_KEY)
    logger.info("Using AnthropicVisionAnalyzer (Claude Vision API)")

_alttext_service = AltTextService(vision_analyzer=_vision_analyzer)


def _get_alttext_service() -> AltTextService:
    return _alttext_service


app.dependency_overrides[images_router.get_alttext_service] = _get_alttext_service

# ── Serve uploaded images ────────────────────────────────────────────
import os

_upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(_upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_upload_dir), name="uploads")

# ── Register Routers ─────────────────────────────────────────────────
app.include_router(rewrite_router.router)
app.include_router(documents_router.router)
app.include_router(analyze_router.router)
app.include_router(images_router.router)


@app.get("/api/health")
async def health_check():
    """Basic health check endpoint."""
    adapter = "fake" if settings.should_use_fake_rewriter else "anthropic"
    return {"status": "ok", "version": "0.2.0", "adapter": adapter}


# ── Test-only endpoint for controlling FakeVisionAnalyzer ────────────
from pydantic import BaseModel


class VisionModeRequest(BaseModel):
    mode: str  # "default", "complex", "outage"


@app.post("/api/test/vision-mode")
async def set_vision_mode(body: VisionModeRequest):
    """Set the FakeVisionAnalyzer mode (test-only)."""
    from adapters.fake_vision_analyzer import FakeVisionAnalyzer

    if isinstance(_vision_analyzer, FakeVisionAnalyzer):
        if body.mode == "complex":
            _vision_analyzer.simulate_complex = True
            _vision_analyzer.simulate_outage = False
        elif body.mode == "outage":
            _vision_analyzer.simulate_outage = True
            _vision_analyzer.simulate_complex = False
        else:
            _vision_analyzer.simulate_outage = False
            _vision_analyzer.simulate_complex = False
            _vision_analyzer._call_count = 0
        return {"status": "ok", "mode": body.mode}
    return {"status": "ignored", "reason": "Not using FakeVisionAnalyzer"}
