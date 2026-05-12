#!/bin/bash
# Start the Gin API backend in the background so the C++ client can hit it
/app/server/backend > /dev/null 2>&1 &
SERVER_PID=$!
sleep 2 

# Run the specific milestone test using pytest
python3 -m pytest tests/test_m${MILESTONE}.py > /dev/null 2>&1
RES=$?

# Kill the server and output exactly 0 or 1
kill $SERVER_PID
if [ $RES -eq 0 ]; then
    echo -n 1
else
    echo -n 0
fi
