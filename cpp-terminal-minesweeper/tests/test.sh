#!/bin/bash
# Start the Gin API backend in the background so the C++ client can hit it
/app/server/backend > /dev/null 2>&1 &
SERVER_PID=$!
sleep 2 

# Default to milestone 1 when the harness does not provide MILESTONE.
MILESTONE="${MILESTONE:-1}"

# Install test-only Python dependencies here (not in the Docker image).
python3 -m pip install --no-cache-dir pytest==8.4.1 requests==2.32.3 > /dev/null 2>&1

# Run the specific milestone test from the mounted /tests directory.
python3 -m pytest -rA /tests/test_m${MILESTONE}.py > /dev/null 2>&1
RES=$?

# Kill the server
kill $SERVER_PID

# The mandatory reward section exactly as the CI demands
if [ $RES -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit $RES
