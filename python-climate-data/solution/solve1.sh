#!/usr/bin/env bash
set -euo pipefail

# Setup the workspace and copy the oracle solution
mkdir -p /app/workspace/src
cp /solution/analyzer.py /app/workspace/src/analyzer.py

# Execute milestone 1 only (cleaned.json)
python3 - <<'EOF'
import sys
sys.path.insert(0, '/app/workspace/src')
from analyzer import milestone_1
milestone_1()
EOF
