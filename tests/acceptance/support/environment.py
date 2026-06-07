"""
Behave environment hooks for UC1 acceptance tests.
Manages the test server, browser, and database lifecycle.
"""

import asyncio
import os
import sys
import threading
import time

import uvicorn

# Add server directory to path
SERVER_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "server")
sys.path.insert(0, SERVER_DIR)


def before_all(context):
    """Start test server with FakeStyleRewriter and launch Playwright browser."""
    from playwright.sync_api import sync_playwright

    from adapters.fake_style_rewriter import FakeStyleRewriter
    from api.routes.rewrite import get_rewrite_service
    from main import app
    from services.rewrite_service import RewriteService

    # ── Inject FakeStyleRewriter ──────────────────────────────────
    context.fake_rewriter = FakeStyleRewriter()
    test_service = RewriteService(style_rewriter=context.fake_rewriter)

    def _get_test_service() -> RewriteService:
        return test_service

    app.dependency_overrides[get_rewrite_service] = _get_test_service

    # ── Start FastAPI in a background thread ──────────────────────
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
    context.server = uvicorn.Server(config)

    thread = threading.Thread(target=context.server.run, daemon=True)
    thread.start()

    # Wait for the server to be ready
    time.sleep(2)

    # ── Launch Playwright browser ─────────────────────────────────
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=True)

    # ── Store the DB helpers module reference ─────────────────────
    from tests.acceptance.support import db_helpers
    context.db_helpers = db_helpers


def before_scenario(context, scenario):
    """Reset database and FakeStyleRewriter state, then open a fresh page."""
    from tests.acceptance.support.db_helpers import reset_db, seed_document

    # Reset FakeStyleRewriter
    context.fake_rewriter.simulate_outage = False

    # Reset database
    asyncio.get_event_loop_policy().new_event_loop()
    loop = asyncio.new_event_loop()

    # Determine scenario-specific seeding
    tags = set(scenario.tags)

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
    """Close the browser page."""
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
