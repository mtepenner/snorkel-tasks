#!/bin/bash
set -e

if [ "$PWD" = "/" ]; then
  echo "Error: No working directory set."
  exit 1
fi

mkdir -p /tmp/test-classes
javac -cp "/usr/share/java/*" /tests/TestOutputs.java -d /tmp/test-classes

set +e
java -cp "/tmp/test-classes:/usr/share/java/*" \
  org.junit.platform.console.ConsoleLauncher \
  --select-class=TestOutputs \
  --fail-if-no-tests

if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
