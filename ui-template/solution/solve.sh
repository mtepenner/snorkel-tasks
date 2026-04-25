#!/bin/bash
# Oracle solution: create the minimal web app at /app for the verifier to serve and test.
mkdir -p /app
cat > /app/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>UI task</title>
  </head>
  <body>
    <h1>Hello, UI task</h1>
    <button>Click me</button>
  </body>
</html>
EOF
