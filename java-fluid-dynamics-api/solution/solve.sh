#!/bin/bash
set -euo pipefail

mkdir -p /app/workspace/src
mkdir -p /app/workspace/data

cp /solution/FluidDynamicsApi.java /app/workspace/src/FluidDynamicsApi.java
cp /solution/postprocess.py /app/workspace/src/postprocess.py