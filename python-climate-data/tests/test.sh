#!/bin/bash
# Validate WORKDIR from Dockerfile.
if [ "$PWD" = "/" ]; then
  echo "Error: No WORKDIR set in Dockerfile."
  exit 1
fi

# Install test dependencies
python3 -m pip install --no-cache-dir uv==0.7.13
uv venv .tbench-testing
source .tbench-testing/bin/activate
uv pip install pytest==8.4.1 \
    pandas==2.0.3 numpy==1.26.4 graphviz==0.20.1

# Prepare logs
mkdir -p /logs/verifier

# Run tests
uv run pytest /tests/ -rA

# Binary reward assignment
if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
