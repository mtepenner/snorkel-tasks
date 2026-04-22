#!/bin/bash

# Ensure the target directories exist
mkdir -p /app/workspace/src/static

# Copy the Oracle solution files into the working directory
cp /app/workspace/solution/api.py /app/workspace/src/api.py
cp /app/workspace/solution/index.html /app/workspace/src/static/index.html

# Start the FastAPI backend in the background so it doesn't block the test runner
cd /app/workspace/src
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &

# Sleep for a few seconds to ensure the server is fully booted before tests run
sleep 3
