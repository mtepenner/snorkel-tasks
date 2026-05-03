#!/bin/bash
set -euo pipefail

mkdir -p /app/workspace/src
mkdir -p /app/workspace/data

cp /solution/FluidDynamicsApi.java /app/workspace/src/FluidDynamicsApi.java
cp /solution/PostProcess.java /app/workspace/src/PostProcess.java