#!/usr/bin/env bash
set -euo pipefail

# Setup the workspace and copy the oracle solution
mkdir -p /app/workspace/src
cp /solution/analyzer.py /app/workspace/src/analyzer.py

# Execute all three milestones (cleaned.json + trends.json + climate_graph.png/.gv)
python3 /app/workspace/src/analyzer.py
