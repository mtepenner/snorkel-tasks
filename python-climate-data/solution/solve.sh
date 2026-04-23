#!/usr/bin/env bash
set -euo pipefail

# Setup the workspace and copy the oracle solution
mkdir -p /app/workspace/src
cp /solution/analyzer.py /app/workspace/src/analyzer.py

# Execute the complete solution
python3 /app/workspace/src/analyzer.py