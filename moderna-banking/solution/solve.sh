#!/bin/bash
mkdir -p /app/workspace/src
cp solution/moderna_banking.cpp /app/workspace/src/moderna_banking.cpp

# Compile the C++ code
g++ -O3 /app/workspace/src/moderna_banking.cpp -o /usr/local/bin/moderna-app
chmod +x /usr/local/bin/moderna-app