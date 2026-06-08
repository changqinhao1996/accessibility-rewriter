"""
Behave environment hooks for UC2 acceptance tests.

UC2 tests run against the already-running frontend (port 5173) and backend (port 8000).
This environment only manages the Playwright browser lifecycle.
"""

import os
import sys


# Add server directory to path for imports
SERVER_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "server")
sys.path.insert(0, SERVER_DIR)


def before_all(context):
    """Launch Playwright browser."""
    from playwright.sync_api import sync_playwright

    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=True)


def before_scenario(context, scenario):
    """Open a fresh browser page for each scenario."""
    context.page = context.browser.new_page()


def after_scenario(context, scenario):
    """Close the browser page."""
    if hasattr(context, "page") and context.page:
        context.page.close()


def after_all(context):
    """Shut down browser."""
    if hasattr(context, "browser"):
        context.browser.close()
    if hasattr(context, "playwright"):
        context.playwright.stop()
