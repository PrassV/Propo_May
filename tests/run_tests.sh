#!/bin/bash

# run_tests.sh - Script to run direct API tests
# This script calls the actual API endpoints without mocks

# Set environment variables for Python warnings
export PYTHONWARNINGS=ignore::DeprecationWarning

# Display test execution information
echo "Running tests with Python $(python --version)"
echo "Testing directly against the API - requires internet connection"

# Check for required packages
echo "Checking required packages..."
pip install pytest pytest-asyncio httpx -q || {
    echo "Error installing required packages"
    exit 1
}

# Run the direct API tests
echo "Running direct API tests..."
python -m pytest tests/simple_test.py -v

# Check the exit code
if [ $? -eq 0 ]; then
    echo "✅ All tests passed successfully!"
else
    echo "❌ Some tests failed. See above for details."
fi 