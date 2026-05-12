#!/bin/bash
set -euo pipefail

# Oracle solution for milestone 1
mkdir -p /app/workspace/src
cp /solution/analyzer.py /app/workspace/src/analyzer.py

python3 - <<'PY'
import importlib.util

spec = importlib.util.spec_from_file_location("analyzer", "/app/workspace/src/analyzer.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.milestone_1()
PY