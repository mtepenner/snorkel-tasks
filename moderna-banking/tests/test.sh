#!/bin/bash

# Check if we're in a valid working directory
if [ "$PWD" = "/" ]; then
    echo "Error: No WORKDIR set. Add WORKDIR to your Dockerfile."
    exit 1
fi

# Install test dependencies
# Wait for apt lock
while fuser /var/lib/dpkg/lock >/dev/null 2>&1 || fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
    echo "Waiting for other software managers to finish..."
    sleep 1
done

apt-get update || true
apt-get install -y python3 python3-pip
pip3 install pytest==8.4.1

# Run pytest with the required -rA flag against the absolute path
pytest -rA /tests/test_outputs.py

# Strict binary reward logic writing exactly to the requested path
if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi