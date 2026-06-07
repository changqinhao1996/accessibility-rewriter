"""
Accessibility & Tone Rewriter — FastAPI Application Entry Point
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import documents as documents_router
from api.routes import rewrite as rewrite_router
from config import settings
from services.rewrite_service import RewriteService

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Accessibility & Tone Rewriter",
    description="API for rewriting text to target reading levels, checking WCAG accessibility, and more.",
    version="0.1.0",
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
#   - Demo / production: real AnthropicStyleRewriter (needs ANTHROPIC_API_KEY)
#   - Tests / offline dev: FakeStyleRewriter (no API key required)

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

# ── Register Routers ─────────────────────────────────────────────────
app.include_router(rewrite_router.router)
app.include_router(documents_router.router)


@app.get("/api/health")
async def health_check():
    """Basic health check endpoint."""
    adapter = "fake" if settings.should_use_fake_rewriter else "anthropic"
    return {"status": "ok", "version": "0.1.0", "adapter": adapter}
