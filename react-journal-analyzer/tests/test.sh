#!/bin/bash
set -e

if [ "$PWD" = "/" ]; then
  echo "Error: No working directory set. Please set a WORKDIR in your Dockerfile before running this script."
  exit 1
fi

# 1. Generate the massive mock Markdown file so the WebServer can serve it
mkdir -p /app/data
echo "# Abstract" > /app/data/paper.md
for i in {1..2000}; do
    echo "This is a massive block of text discussing quantum mechanics and entanglement. Here is a citation [$i]." >> /app/data/paper.md
done
echo "# Conclusion" >> /app/data/paper.md
echo "Final thoughts on quantum entanglement [2001]." >> /app/data/paper.md

# 2. Run the provided UI skeleton test suite
cd /tests
npm install
export DEBIAN_FRONTEND=noninteractive
npx playwright install-deps chromium
npx playwright install chromium

UNIT_EXIT=0
E2E_EXIT=0
npm run test || UNIT_EXIT=$?
npm run test:e2e || E2E_EXIT=$?

mkdir -p /logs/verifier
if [ "$UNIT_EXIT" -eq 0 ] && [ "$E2E_EXIT" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

[ "$UNIT_EXIT" -eq 0 ] && [ "$E2E_EXIT" -eq 0 ]
