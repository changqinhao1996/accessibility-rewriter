"""
Behave environment hooks for acceptance tests.
Manages the test server, browser, and database lifecycle.

UC1 scenarios: Start embedded server + seed DB
UC2 scenarios: Use already-running external servers (no DB modification)
UC3 scenarios: Use already-running external servers + seed images DB
"""

import asyncio
import os
import sys
import threading
import time

import requests
import uvicorn

# Add server directory to path
SERVER_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "server")
sys.path.insert(0, SERVER_DIR)

# Add project root to path so tests.acceptance imports work
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.insert(0, os.path.abspath(PROJECT_ROOT))


def _is_uc2_only(context):
    """Check if we are running only UC2 tests (no embedded server needed)."""
    return getattr(context, "_uc2_mode", False)


def _is_uc3_mode(context):
    """Check if we are running UC3 tests."""
    return getattr(context, "_uc3_mode", False)


def _run_async(coro):
    """Run an async function in a new event loop."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def before_all(context):
    """Start test server with FakeStyleRewriter and launch Playwright browser."""
    from playwright.sync_api import sync_playwright

    # ── Detect mode ──────────────────────────────────────────────────
    uc2_mode = context.config.userdata.get("UC2", "false").lower() == "true"
    uc3_mode = context.config.userdata.get("UC3", "false").lower() == "true"
    context._uc2_mode = uc2_mode
    context._uc3_mode = uc3_mode

    if not uc2_mode and not uc3_mode:
        from adapters.fake_style_rewriter import FakeStyleRewriter
        from api.routes.rewrite import get_rewrite_service
        from main import app
        from services.rewrite_service import RewriteService

        # ── Inject FakeStyleRewriter ──────────────────────────────
        context.fake_rewriter = FakeStyleRewriter()
        test_service = RewriteService(style_rewriter=context.fake_rewriter)

        def _get_test_service() -> RewriteService:
            return test_service

        app.dependency_overrides[get_rewrite_service] = _get_test_service

        # ── Start FastAPI in a background thread ──────────────────
        config = uvicorn.Config(
            app, host="127.0.0.1", port=8000, log_level="warning"
        )
        context.server = uvicorn.Server(config)

        thread = threading.Thread(target=context.server.run, daemon=True)
        thread.start()

        # Wait for the server to be ready
        time.sleep(2)

        # ── Store the DB helpers module reference ─────────────────
        from tests.acceptance.support import db_helpers

        context.db_helpers = db_helpers

    if uc3_mode:
        # ── Configure FakeVisionAnalyzer via API ──────────────────
        # UC3 uses already-running external servers.
        # The FakeVisionAnalyzer is injected server-side via main.py
        # We just need to seed the DB and manage state.
        pass

    # ── Launch Playwright browser ─────────────────────────────────
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=True)


def before_scenario(context, scenario):
    """Reset database and state, then open a fresh page."""
    tags = set(scenario.tags)

    # ── UC3 scenarios ─────────────────────────────────────────────
    if "UC3" in tags or any(t.startswith("UC3-") for t in tags):
        from tests.acceptance.support.uc3_db_helpers import (
            ensure_seed_document_exists,
            reset_images_table,
            seed_image,
        )

        # Reset images table (synchronous calls)
        reset_images_table()
        ensure_seed_document_exists()

        # Seed based on scenario tags
        if "UC3-S06" in tags:
            # Two images without alt text
            seed_image(filename="landscape.png")
            seed_image(filename="apple.png")
        elif "UC3-S12" in tags:
            # All images already described
            seed_image(
                filename="landscape.png",
                alt_text="A scenic landscape",
                alt_text_status="described",
            )
        elif "UC3-S14" in tags:
            # No images at all — don't seed
            pass
        elif "UC3-S09" in tags or "UC3-S15" in tags or "UC3-S19" in tags:
            # Complex image — seed infographic
            seed_image(filename="infographic.png")
            # Set FakeVisionAnalyzer to complex mode via endpoint
            try:
                requests.post(
                    "http://localhost:8000/api/test/vision-mode",
                    json={"mode": "complex"},
                    timeout=2,
                )
            except Exception:
                pass
        elif "UC3-S10" in tags:
            # AI service unavailable
            seed_image(filename="landscape.png")
            try:
                requests.post(
                    "http://localhost:8000/api/test/vision-mode",
                    json={"mode": "outage"},
                    timeout=2,
                )
            except Exception:
                pass
        elif "UC3-S22" in tags:
            # Apple image
            seed_image(filename="apple.png")
        elif "UC3-S24" in tags:
            # Bar chart
            seed_image(filename="barchart.png")
        else:
            # Default: one image without alt text
            seed_image(filename="landscape.png")

        # Open a fresh browser page
        context.page = context.browser.new_page()
        return

    # ── UC2 scenarios: just open a browser page ───────────────────
    if "UC2" in tags or any(t.startswith("UC2-") for t in tags):
        context.page = context.browser.new_page()
        return

    # ── UC1 scenarios: full DB reset + seeding ────────────────────
    from tests.acceptance.support.db_helpers import reset_db, seed_document

    # Reset FakeStyleRewriter
    context.fake_rewriter.simulate_outage = False

    # Reset database
    asyncio.get_event_loop_policy().new_event_loop()
    loop = asyncio.new_event_loop()

    if "UC1-S05" in tags:
        # No document loaded
        loop.run_until_complete(reset_db())
        context.document_id = None
    elif "UC1-S06" in tags:
        # Document with empty content
        loop.run_until_complete(reset_db())
        doc_id = loop.run_until_complete(seed_document(content=""))
        context.document_id = doc_id
    elif "UC1-S07" in tags:
        # Document with whitespace-only content
        loop.run_until_complete(reset_db())
        doc_id = loop.run_until_complete(seed_document(content="   \n\t  "))
        context.document_id = doc_id
    elif "UC1-S09" in tags or "UC1-S15" in tags:
        # Document with UNCLEAR_SENTINEL
        loop.run_until_complete(reset_db())
        doc_id = loop.run_until_complete(
            seed_document(content="UNCLEAR_SENTINEL ambiguous text here")
        )
        context.document_id = doc_id
        if "UC1-S15" in tags:
            from tests.acceptance.support.db_helpers import seed_version

            loop.run_until_complete(
                seed_version(doc_id, version_number=1, content="v1 content")
            )
    elif "UC1-S10" in tags:
        # Service outage
        loop.run_until_complete(reset_db())
        doc_id = loop.run_until_complete(seed_document())
        context.document_id = doc_id
        context.fake_rewriter.simulate_outage = True
    elif "UC1-S13" in tags:
        # Document with 2 existing versions
        loop.run_until_complete(reset_db())
        doc_id = loop.run_until_complete(seed_document())
        context.document_id = doc_id
        from tests.acceptance.support.db_helpers import seed_version

        loop.run_until_complete(
            seed_version(doc_id, version_number=1, content="Version 1 text")
        )
        loop.run_until_complete(
            seed_version(doc_id, version_number=2, content="Version 2 text")
        )
        # Snapshot existing versions for later comparison
        from tests.acceptance.support.db_helpers import get_versions

        context.prior_versions = loop.run_until_complete(get_versions(doc_id))
    elif "UC1-S14" in tags:
        # Document with 1 existing version
        loop.run_until_complete(reset_db())
        doc_id = loop.run_until_complete(seed_document())
        context.document_id = doc_id
        from tests.acceptance.support.db_helpers import seed_version

        loop.run_until_complete(
            seed_version(doc_id, version_number=1, content="Version 1 text")
        )
    else:
        # Default: seed a standard document
        loop.run_until_complete(reset_db())
        doc_id = loop.run_until_complete(seed_document())
        context.document_id = doc_id

    loop.close()

    # ── Open a fresh browser page ─────────────────────────────────
    context.page = context.browser.new_page()

    if context.document_id:
        # Navigate with the document ID so RewritePage loads it
        base_url = f"http://localhost:5173?doc={context.document_id}"
    else:
        base_url = "http://localhost:5173"

    context.page.goto(base_url)
    context.page.wait_for_load_state("networkidle")


def after_scenario(context, scenario):
    """Close the browser page and reset vision analyzer mode."""
    tags = set(scenario.tags)

    # Reset FakeVisionAnalyzer after UC3 scenarios
    if "UC3" in tags or any(t.startswith("UC3-") for t in tags):
        try:
            requests.post(
                "http://localhost:8000/api/test/vision-mode",
                json={"mode": "default"},
                timeout=2,
            )
        except Exception:
            pass

    if hasattr(context, "page") and context.page:
        context.page.close()


def after_all(context):
    """Shut down browser and test server."""
    if hasattr(context, "browser"):
        context.browser.close()
    if hasattr(context, "playwright"):
        context.playwright.stop()
    if hasattr(context, "server"):
        context.server.should_exit = True
