#!/bin/sh

# Make sure pytest-asyncio is installed
pip install pytest-asyncio httpx

# Run the direct API tests
python -m pytest -v --no-header tests/simple_test.py 