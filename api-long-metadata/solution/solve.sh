#!/bin/bash
set -euo pipefail

mkdir -p /app/workspace/src/static

# Correctly pull from the isolated harness mount
cp /solution/api.py /app/workspace/src/api.py
cp /solution/index.html /app/workspace/src/static/index.html

cd /app/workspace/src
# Start the server in the background
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &

# Poll until the server is actively accepting connections (max 15 seconds)
for i in $(seq 1 15); do
  sleep 1
  curl -sf http://localhost:8000/static/index.html > /dev/null 2>&1 && break
done