"""
Root test configuration.
Shared fixtures for acceptance, unit, and integration tests.
"""

import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio as the async backend for tests."""
    return "asyncio"
