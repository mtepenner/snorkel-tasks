#!/bin/bash
set -eu

if [ "$PWD" = "/" ]; then
    echo "Error: No working directory set. Please set a WORKDIR in your Dockerfile before running this script."
    exit 1
fi

g++ -std=c++17 -Wall -Wextra -pedantic /tests/test_outputs.cpp -o /tmp/circular_linked_list_verifier

set +e
/tmp/circular_linked_list_verifier

if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi