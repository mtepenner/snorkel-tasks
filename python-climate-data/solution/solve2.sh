#!/usr/bin/env bash
set -euo pipefail

# Setup the workspace and copy the oracle solution
mkdir -p /app/workspace/src
cp /solution/analyzer.py /app/workspace/src/analyzer.py

# Execute milestones 1 and 2 (cleaned.json + trends.json)
python3 - <<'EOF'
import sys
sys.path.insert(0, '/app/workspace/src')
from analyzer import milestone_1, milestone_2
df = milestone_1()
milestone_2(df)
EOF
