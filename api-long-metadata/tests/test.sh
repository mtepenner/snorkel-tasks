#!/bin/bash

# Bootstrap uv into the container without shelling out to curl.
python3 -m pip install --no-cache-dir uv==0.7.13 > /dev/null 2>&1

server_ready() {
  python3 - <<'PY'
import sys
import urllib.request

try:
    with urllib.request.urlopen("http://localhost:8000/static/index.html", timeout=1) as response:
        raise SystemExit(0 if response.status == 200 else 1)
except Exception:
    raise SystemExit(1)
PY
}

if [ "$PWD" = "/" ]; then
  echo "Error: No working directory set."
  exit 1
fi

SERVER_PID=""
trap 'if [ -n "$SERVER_PID" ]; then kill "$SERVER_PID" 2>/dev/null || true; fi' EXIT

if ! server_ready; then
  cd /app/workspace/src
  python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &
  SERVER_PID=$!

  for i in $(seq 1 15); do
    sleep 1
    server_ready && break
  done

  cd - > /dev/null
fi

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
