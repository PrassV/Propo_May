#!/usr/bin/env python
import os
import subprocess

# Get PORT from environment variable or use 8000 as default
port = os.environ.get('PORT', '8000')

# Start uvicorn with the correct port
subprocess.run([
    'python', '-m', 'uvicorn', 
    'app.main:app', 
    '--host=0.0.0.0', 
    f'--port={port}',
    '--timeout-keep-alive=300'
]) 