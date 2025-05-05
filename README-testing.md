# API Testing Framework

This document explains the direct API testing framework for the Property Management Portal API.

## Overview

Our testing framework uses pytest and httpx to directly test API endpoints without mocks. This approach offers several advantages:

1. Tests actual API behavior in the real environment
2. Validates true API responses and status codes
3. Detects real-world issues like network problems or server unavailability
4. Requires minimal maintenance - no mocks to update when API changes

## Key Components

### 1. Direct HTTP Client

The tests use `httpx.AsyncClient` to make real HTTP requests to the API. This allows us to:
- Test actual API endpoints
- Verify real response status codes
- Check actual response data formats
- Validate error handling

### 2. Focused Test Cases

Tests are designed to be focused and specific:
- Each test verifies a specific aspect of the API
- Tests include proper assertions with clear error messages
- Tests handle network and server errors gracefully
- Tests are isolated from each other

### 3. Async Testing

Tests use Python's async features via pytest-asyncio:
- Async HTTP requests for efficient testing
- Proper resource management with async context managers
- Supports making multiple parallel requests if needed

## Running Tests

Use the provided `run_tests.sh` script to run all tests:

```bash
./tests/run_tests.sh
```

The script:
1. Configures the Python environment
2. Checks for required packages
3. Executes the direct API tests
4. Displays a summary of results

## Test Organization

Tests are organized in `simple_test.py` focusing on key API behaviors:

1. `test_unauthorized_access` - Verifies that protected endpoints require authentication
2. `test_api_server_availability` - Confirms the API server is online and responding

## Adding New Tests

When adding new tests:

1. Create a new async test function with the `@pytest.mark.asyncio` decorator
2. Use httpx.AsyncClient to make direct API requests
3. Add clear assertions that validate the expected behavior
4. Use logging to track test execution and results
5. Handle errors gracefully with informative failure messages

## Troubleshooting

If tests fail:

1. Check server availability at the API URL
2. Verify your internet connection
3. Check the API endpoint path is correct
4. Inspect the full error message and response content
5. Verify any authentication credentials

## Best Practices

1. Keep tests lightweight - focus on one aspect per test
2. Use descriptive test names
3. Log important steps and results
4. Handle expected errors gracefully
5. Make sure tests are isolated from each other
6. Use proper async/await patterns
7. Clean up any resources created during testing 