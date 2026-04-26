#!/bin/bash
set -euo pipefail

echo "Running full ML Model Management setup..."
mkdir -p /app/workspace/src/templates

cp /solution/api.py /app/workspace/src/api.py

cp /solution/index.html /app/workspace/src/templates/index.html

echo "Setup complete."
