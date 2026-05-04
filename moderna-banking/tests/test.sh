#!/bin/bash

# Install test dependencies
pip3 install pytest==8.4.1

# Run pytest with the required -rA flag against the absolute path
pytest -rA /tests/test_outputs.py

# Strict binary reward logic writing exactly to the requested path
if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi