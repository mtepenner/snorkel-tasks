#!/bin/bash
set -euo pipefail

echo "Running full ML Model Management setup..."
mkdir -p /app/workspace/src/templates
mkdir -p /app/workspace/src/static/js

cp /solution/ml_model_mgmt_server.cpp /app/workspace/src/ml_model_mgmt_server.cpp

cp /solution/index.html /app/workspace/src/templates/index.html

echo "Setup complete."
