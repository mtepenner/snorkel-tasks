#!/bin/bash
set -euo pipefail
mkdir -p /app/workspace
cp /solution/main.cpp /app/workspace/main.cpp

# Compile the C++ code
g++ -O3 /app/workspace/main.cpp -o /app/workspace/vacation-app
chmod +x /app/workspace/vacation-app
