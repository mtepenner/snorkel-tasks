#!/bin/bash

# Install uv dependencies
apt-get update > /dev/null 2>&1
apt-get install -y curl > /dev/null 2>&1

# Bootstrap uv into the container
curl -LsSf https://astral.sh/uv/0.7.13/install.sh | sh > /dev/null 2>&1
source $HOME/.local/bin/env

if [ "$PWD" = "/" ]; then
  echo "Error: No working directory set."
  exit 1
fi

# Start the API server (uvicorn is pre-installed in the Docker image)
cd /app/workspace/src
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &
SERVER_PID=$!

# Poll until the server is accepting connections (max 15 seconds)
for i in $(seq 1 15); do
  sleep 1
  curl -sf http://localhost:8000/static/index.html > /dev/null 2>&1 && break
done

cd -

# Run tests using pinned dependencies and the correct harness mount path
uvx \
  -p 3.13 \
  --with pytest==8.4.1 \
  --with pytest-json-ctrf==0.3.5 \
  --with requests==2.32.3 \
  --with fpdf2==2.8.3 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA

# Produce reward file (REQUIRED)
if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
