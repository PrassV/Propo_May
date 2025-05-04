"""
Pytest configuration file.

This file contains global pytest configuration for the test suite.
"""
import pytest
import logging
import os
import sys
from typing import Dict, Any, Optional, List

# Add the parent directory to sys.path to allow importing from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Suppress overly verbose logs during tests
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Define pytest hooks
def pytest_configure(config):
    """Configure pytest before test collection."""
    print("\nRunning Authentication and User Management API Tests...\n")


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 