#!/bin/bash
# Solve script for Milestone 2

echo "Setting up Milestone 2 (Frontend UI)..."
mkdir -p /app/workspace/src/templates
mkdir -p /app/workspace/src/static/js
mkdir -p /app/workspace/src/static/css

cp /app/workspace/solution/index.html /app/workspace/src/templates/index.html

# Only copy static files if they are broken out of index.html in your solution
if [ -f /app/workspace/solution/app.js ]; then
    cp /app/workspace/solution/app.js /app/workspace/src/static/js/app.js
fi
if [ -f /app/workspace/solution/styles.css ]; then
    cp /app/workspace/solution/styles.css /app/workspace/src/static/css/styles.css
fi
echo "Milestone 2 setup complete."
