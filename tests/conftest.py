"""
Pytest configuration file for direct API testing.

This file contains global pytest configuration for the API test suite.
"""
import pytest
import pytest_asyncio
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Suppress overly verbose logs during tests
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Register pytest-asyncio plugin
pytest_plugins = ["pytest_asyncio"]

def pytest_configure(config):
    """Configure pytest before test collection."""
    print("\nRunning Direct API Tests...\n")

# pytest-asyncio will automatically detect mode from command line or pytest.ini
# Don't try to set it programmatically here 