#!/bin/bash

# Check if we're in a valid working directory
if [ "$PWD" = "/" ]; then
    echo "Error: No WORKDIR set. Add WORKDIR to your Dockerfile."
    exit 1
fi

# Aggressively clear locks (in case of background auto-updates in ephemeral container test)
killall -9 apt apt-get dpkg unattended-upgrades 2>/dev/null || true
rm -f /var/lib/apt/lists/lock
rm -f /var/cache/apt/archives/lock
rm -f /var/lib/dpkg/lock-frontend
rm -f /var/lib/dpkg/lock
dpkg --configure -a || true

# Install test dependencies
apt-get update -y || true
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