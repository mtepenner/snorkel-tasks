#!/bin/bash

echo "Running full ML Model Management setup..."
mkdir -p /app/workspace/src/templates
mkdir -p /app/workspace/src/static/js
mkdir -p /app/workspace/src/static/css

cp /app/workspace/solution/api.py /app/workspace/src/api.py

cp /app/workspace/solution/index.html /app/workspace/src/templates/index.html

if [ -f /app/workspace/solution/app.js ]; then
    cp /app/workspace/solution/app.js /app/workspace/src/static/js/app.js
fi
if [ -f /app/workspace/solution/styles.css ]; then
    cp /app/workspace/solution/styles.css /app/workspace/src/static/css/styles.css
fi

echo "Setup complete."
