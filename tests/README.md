# Authentication and User Management API Tests

This directory contains automated tests for the authentication and user management endpoints of the Property Management Portal API.

## Overview

The test suite uses pytest and the MCP (Model Context Protocol) server to test the API endpoints thoroughly.

### Structure

- `mcp_client.py`: Client for communicating with the MCP server
- `auth_test_base.py`: Base class for auth tests with common functionality
- `test_auth_endpoints.py`: Tests for authentication endpoints
- `test_user_endpoints.py`: Tests for user management endpoints
- `test_auth_scenarios.py`: End-to-end auth scenario tests
- `conftest.py`: Pytest configuration

## Requirements

- Python 3.8+
- pytest
- pytest-asyncio
- httpx

## Installation

```bash
# Install dependencies
pip install pytest pytest-asyncio httpx
```

## Running Tests

To run all tests:

```bash
# From the project root directory
pytest tests/

# With more verbose output
pytest -v tests/

# Run specific test file
pytest tests/test_auth_endpoints.py

# Run specific test
pytest tests/test_auth_endpoints.py::TestAuthEndpoints::test_user_registration
```

## MCP Server Integration

The tests use the MCP server at `https://propomay-production.up.railway.app/mcp` to perform database operations. The MCP server provides these tools:

- `execute_query`: Run SQL queries
- `insert_data`: Insert data into tables
- `update_data`: Update existing records
- `delete_data`: Delete records
- `describe_schema`: Get database schema info

## Test Cleanup

The tests automatically clean up any test data they create. If you need to manually clean up test data, you can use:

```python
# From the Python interpreter
import asyncio
from tests.mcp_client import MCPClient

async def cleanup():
    client = MCPClient()
    await client.clean_up_test_users("test_user_%")
    await client.close()

asyncio.run(cleanup())
``` 