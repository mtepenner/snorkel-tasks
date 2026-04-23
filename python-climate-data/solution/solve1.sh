#!/bin/bash
mkdir -p /app/workspace/src
cp /solution/analyzer.py /app/workspace/src/analyzer.py

python3 -c "
import sys
sys.path.insert(0, '/app/workspace/src')
import analyzer
analyzer.milestone_1()
"