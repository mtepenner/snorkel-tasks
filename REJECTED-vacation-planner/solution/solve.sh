#!/bin/bash
set -euo pipefail
mkdir -p /app/workspace/src
cp /solution/main.cpp /app/workspace/src/vacation_planner.cpp

# Compile the C++ code
g++ -O3 /app/workspace/src/vacation_planner.cpp -o /usr/local/bin/vacation-app
chmod +x /usr/local/bin/vacation-app
