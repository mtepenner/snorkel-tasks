#!/bin/bash
# Start the Gin API backend in the background so the C++ client can hit it
/app/server/backend > /dev/null 2>&1 &
SERVER_PID=$!
sleep 2 

# Run the specific milestone test using pytest with the mandatory -rA flag
python3 -m pytest -rA tests/test_m${MILESTONE}.py > /dev/null 2>&1
RES=$?

# Kill the server
kill $SERVER_PID

# Reset the exit code to the pytest result so the required block works
(exit $RES)

# The mandatory reward section exactly as the CI demands
if [ $? -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
