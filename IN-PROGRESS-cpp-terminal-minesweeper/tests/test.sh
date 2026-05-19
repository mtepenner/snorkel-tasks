#!/bin/bash
/app/server/backend > /tmp/server.log 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null || true' EXIT
sleep 2 
mkdir -p /app/workspace/data/replays
python3 -m pip install --no-cache-dir pytest==8.4.1 requests==2.32.3 > /dev/null 2>&1
python3 -m pytest -rA /tests/test_outputs.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
