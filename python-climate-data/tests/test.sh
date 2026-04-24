#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"

# Ensure the logs directory exists
mkdir -p /logs/verifier

MILESTONE=$1

if [ "$MILESTONE" == "1" ]; then
    pytest /root/tasks/tbench-task/tests/test_m1.py -rA > /dev/null 2>&1
elif [ "$MILESTONE" == "2" ]; then
    pytest /root/tasks/tbench-task/tests/test_m2.py -rA > /dev/null 2>&1
elif [ "$MILESTONE" == "3" ]; then
    pytest /root/tasks/tbench-task/tests/test_m3.py -rA > /dev/null 2>&1
else
    # Run all sequentially if no specific milestone is provided
    pytest /root/tasks/tbench-task/tests/test_m1.py -rA && \
    pytest /root/tasks/tbench-task/tests/test_m2.py -rA && \
    pytest /root/tasks/tbench-task/tests/test_m3.py -rA > /dev/null 2>&1
fi

# Strict Terminus binary reward assignment
if [ $? -eq 0 ]; then
    echo 1.0 > /logs/verifier/reward.txt
    exit 0
else
    echo 0.0 > /logs/verifier/reward.txt
    exit 1
fi
