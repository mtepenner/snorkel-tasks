#!/bin/bash

echo "Running full ML Model Management setup..."
mkdir -p /app/workspace/src/templates
mkdir -p /app/workspace/src/static/js
mkdir -p /app/workspace/src/static/css

cp /solution/api.py /app/workspace/src/api.py

cp /solution/index.html /app/workspace/src/templates/index.html

if [ -f /solution/app.js ]; then
    cp /solution/app.js /app/workspace/src/static/js/app.js
fi
if [ -f /solution/styles.css ]; then
    cp /solution/styles.css /app/workspace/src/static/css/styles.css
fi

echo "Setup complete."
