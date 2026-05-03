#!/bin/bash
set -e

apt-get update -qq
apt-get install -y --no-install-recommends curl

if [ "$PWD" = "/" ]; then
    echo "Error: No working directory set. Please set a WORKDIR in your Dockerfile before running this script."
    exit 1
fi

JUNIT_JAR=/tmp/junit-platform-console-standalone-1.11.4.jar
GSON_JAR=/tmp/gson-2.10.1.jar

echo "==> Downloading JUnit..."
curl -fsSL --retry 3 \
    "https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.11.4/junit-platform-console-standalone-1.11.4.jar" \
    -o "$JUNIT_JAR"
echo "    junit jar: $(stat -c%s "$JUNIT_JAR") bytes"

echo "==> Downloading Gson..."
curl -fsSL --retry 3 \
    "https://repo1.maven.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar" \
    -o "$GSON_JAR"
echo "    gson jar: $(stat -c%s "$GSON_JAR") bytes"

mkdir -p /tmp/test-classes
echo "==> Compiling TestOutputs.java..."
javac -cp "$JUNIT_JAR:$GSON_JAR" /tests/TestOutputs.java -d /tmp/test-classes

echo "==> Running tests..."
set +e
java -cp "/tmp/test-classes:$JUNIT_JAR:$GSON_JAR" \
    org.junit.platform.console.ConsoleLauncher \
    --select-class=TestOutputs \
    --fail-if-no-tests

if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
