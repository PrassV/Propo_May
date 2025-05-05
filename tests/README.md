# Direct API Testing for Property Management Portal

This directory contains automated tests that directly test the API endpoints of the Property Management Portal.

## Overview

The test suite uses pytest, pytest-asyncio, and httpx to make real HTTP requests to the API endpoints. This approach:

1. Tests actual API behavior in the real environment
2. Validates true API responses and status codes
3. Detects real-world issues like network problems or server unavailability
4. Requires minimal maintenance - no mocks to update when API changes

## Structure

- `simple_test.py`: Direct API tests for key functionality
- `conftest.py`: Pytest configuration for the test suite
- `run_tests.sh`: Script to run the tests

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
./tests/run_tests.sh

# Or manually with pytest
python -m pytest tests/simple_test.py -v
```

## Test Cases

The current test suite includes:

1. `test_unauthorized_access`: Verifies that protected endpoints require authentication
2. `test_api_server_availability`: Confirms the API server is online and responding

## Adding New Tests

When adding new tests:

1. Add them to `simple_test.py` or create new test files as needed
2. Use the `@pytest.mark.asyncio` decorator for async test functions
3. Make HTTP requests using `httpx.AsyncClient`
4. Add clear assertions that validate expected behavior
5. Handle errors gracefully with informative messages 